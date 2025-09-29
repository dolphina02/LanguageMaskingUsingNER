# Databricks 환경에서 GLiNER 기반 개인정보 마스킹 UDF
# 필요 패키지: pip install gliner pyspark pandas

from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf, col
from pyspark.sql.types import StringType
import pandas as pd
import re

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("GLiNER_PII_Masking") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

# 부분 마스킹 함수들
def mask_name(name):
    """이름 부분 마스킹: 홍길동 → 홍*동"""
    if len(name) <= 1:
        return name
    elif len(name) == 2:
        return name[0] + '*'
    else:
        return name[0] + '*' * (len(name) - 2) + name[-1]

def mask_phone(phone):
    """전화번호 부분 마스킹"""
    if '-' in phone:
        parts = phone.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]}-****"
    return phone[:7] + '****' if len(phone) > 7 else phone

def mask_resident_number(rrn):
    """주민번호 부분 마스킹"""
    if '-' in rrn:
        front, back = rrn.split('-')
        return front + '-' + back[0] + '*' * (len(back) - 1)
    elif len(rrn) == 13:
        return rrn[:7] + '*' * 6
    return rrn

def partial_mask_entity(text, entity_type):
    """엔티티 타입에 따른 부분 마스킹"""
    if entity_type in ["PERSON", "PER"]:
        clean_text = re.sub(r'[은는이가을를에게께서님씨군양]$', '', text)
        suffix = text[len(clean_text):]
        return mask_name(clean_text) + suffix
    elif entity_type in ["PHONE"]:
        return mask_phone(text)
    elif entity_type in ["ID", "RESIDENT_NUMBER"]:
        return mask_resident_number(text)
    elif entity_type in ["ORGANIZATION", "ORG"]:
        return mask_name(text)
    elif entity_type in ["LOCATION", "LOC"]:
        return mask_name(text)
    else:
        return mask_name(text)

# 싱글톤 패턴으로 모델 로딩 (성능 최적화)
class GLiNERModelSingleton:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GLiNERModelSingleton, cls).__new__(cls)
        return cls._instance
    
    def get_model(self):
        if self._model is None:
            try:
                from gliner import GLiNER
                print("GLiNER 모델 로딩 중...")
                self._model = GLiNER.from_pretrained("taeminlee/gliner_ko")
                print("GLiNER 모델 로딩 완료!")
            except Exception as e:
                print(f"GLiNER 모델 로딩 실패: {e}")
                self._model = None
        return self._model

# 정규식 기반 백업 마스킹 (GLiNER 실패 시)
def regex_based_masking(text):
    """정규식 기반 백업 마스킹"""
    masked_text = text
    
    # 주민번호 패턴 (한글 숫자 포함)
    rrn_patterns = [
        r'[가-힣]*[영일이삼사오육칠팔구공하나둘셋넷다섯여섯일곱여덟아홉]{13,}',
        r'\d{6}-\d{7}',
        r'\d{13}'
    ]
    
    for pattern in rrn_patterns:
        matches = list(re.finditer(pattern, masked_text))
        for match in reversed(matches):  # 뒤에서부터 처리
            original = match.group()
            if len(original) >= 10:  # 주민번호로 추정되는 길이
                masked = original[:6] + '*' * (len(original) - 6)
                masked_text = masked_text[:match.start()] + masked + masked_text[match.end():]
    
    # 한국 이름 패턴
    name_pattern = r'[가-힣]{2,4}(?=은|는|이|가|을|를|에게|께서|님|씨)'
    matches = list(re.finditer(name_pattern, masked_text))
    for match in reversed(matches):
        original = match.group()
        masked = mask_name(original)
        masked_text = masked_text[:match.start()] + masked + masked_text[match.end():]
    
    return masked_text

# 방법 1: 일반 UDF (권장)
from pyspark.sql.functions import udf

@udf(StringType())
def gliner_mask_udf(text):
    """GLiNER 기반 개인정보 마스킹 UDF (일반 UDF)"""
    
    if not text or len(text.strip()) == 0:
        return text
    
    # 모델 로딩 (싱글톤 패턴)
    model_singleton = GLiNERModelSingleton()
    model = model_singleton.get_model()
    
    try:
        if model is not None:
            # GLiNER 모델 사용
            labels = ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "PHONE", "ID"]
            entities = model.predict_entities(text, labels)
            
            # 신뢰도 0.8 이상인 엔티티만 마스킹
            sensitive_entities = [e for e in entities if e.get("score", 0) >= 0.8]
            
            # 위치별 역순 정렬
            sensitive_entities = sorted(sensitive_entities, key=lambda e: e['start'], reverse=True)
            
            masked_text = text
            for entity in sensitive_entities:
                original_text = entity['text']
                entity_type = entity['label']
                masked_entity = partial_mask_entity(original_text, entity_type)
                masked_text = masked_text[:entity['start']] + masked_entity + masked_text[entity['end']:]
            
            return masked_text
        else:
            # GLiNER 실패 시 정규식 백업
            return regex_based_masking(text)
            
    except Exception as e:
        print(f"마스킹 처리 중 오류: {e}")
        # 오류 시 정규식 백업
        return regex_based_masking(text)

# 방법 2: pandas_udf (대용량 데이터용)
@pandas_udf(StringType())
def gliner_mask_pandas_udf(texts: pd.Series) -> pd.Series:
    """GLiNER 기반 개인정보 마스킹 pandas_udf (대용량 데이터용)"""
    
    # 배치 시작 시 한 번만 모델 로딩
    model_singleton = GLiNERModelSingleton()
    model = model_singleton.get_model()
    
    def mask_single_text(text):
        if not text or len(text.strip()) == 0:
            return text
            
        try:
            if model is not None:
                labels = ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "PHONE", "ID"]
                entities = model.predict_entities(text, labels)
                
                sensitive_entities = [e for e in entities if e.get("score", 0) >= 0.8]
                sensitive_entities = sorted(sensitive_entities, key=lambda e: e['start'], reverse=True)
                
                masked_text = text
                for entity in sensitive_entities:
                    original_text = entity['text']
                    entity_type = entity['label']
                    masked_entity = partial_mask_entity(original_text, entity_type)
                    masked_text = masked_text[:entity['start']] + masked_entity + masked_text[entity['end']:]
                
                return masked_text
            else:
                return regex_based_masking(text)
                
        except Exception as e:
            return regex_based_masking(text)
    
    return texts.apply(mask_single_text)

# 테스트 데이터
data = [
    (1, "상담사", "다음 동의는 가입 설계 및 맞춤형 보험 상담 기존 계약과 비교 안내를 위한 선택 사항으로 거부 가능하며 거부 시 자세한 상담이 어려울 수 있습니다."),
    (2, "고객", "네 주민번호는 팔오하나둘일구 둘둘삼삼하나하나육 이에요"),
    (3, "상담사", "아 넵.. 팔오하나둘일구 둘둘삼삼하나하나육"),
    (4, "고객", "홍길동이고 전화번호는 010-1234-5678입니다."),
    (5, "상담사", "김철수님 안녕하세요. 서울 강남구에 거주하시는군요.")
]

# DataFrame 생성
df = spark.createDataFrame(data, ["line_id", "speaker", "text"])

# 마스킹 적용 - 두 가지 방법 중 선택

# 방법 1: 일반 UDF 사용 (권장 - 안정성 우선)
df_masked = df.withColumn("masked_text", gliner_mask_udf(col("text")))

# 방법 2: pandas_udf 사용 (대용량 데이터 시)
# df_masked = df.withColumn("masked_text", gliner_mask_pandas_udf(col("text")))

# 파일 처리 함수들 추가
def process_text_files_from_dbfs(input_path, output_path, file_format="text"):
    """DBFS에서 텍스트 파일들을 읽어서 마스킹 후 저장"""
    
    print(f"📂 DBFS 파일 읽기: {input_path}")
    
    try:
        if file_format == "text":
            # 텍스트 파일 읽기 (각 줄이 하나의 레코드)
            df = spark.read.text(input_path)
            df = df.withColumn("line_id", monotonically_increasing_id())
            df = df.select("line_id", col("value").alias("text"))
            
        elif file_format == "csv":
            # CSV 파일 읽기
            df = spark.read.option("header", "true").csv(input_path)
            df = df.withColumn("line_id", monotonically_increasing_id())
            
        elif file_format == "json":
            # JSON 파일 읽기
            df = spark.read.json(input_path)
            df = df.withColumn("line_id", monotonically_increasing_id())
            
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_format}")
        
        print(f"📊 총 {df.count()}개 레코드 로드됨")
        
        # 텍스트 컬럼이 있는지 확인
        text_columns = [col_name for col_name in df.columns if 'text' in col_name.lower() or 'content' in col_name.lower()]
        if not text_columns:
            text_columns = [col_name for col_name in df.columns if col_name not in ['line_id']]
        
        if not text_columns:
            raise ValueError("텍스트 컬럼을 찾을 수 없습니다.")
        
        text_column = text_columns[0]  # 첫 번째 텍스트 컬럼 사용
        print(f"📝 텍스트 컬럼 사용: {text_column}")
        
        # 마스킹 적용
        print("🔒 마스킹 처리 시작...")
        df_masked = df.withColumn("masked_text", gliner_mask_udf(col(text_column)))
        
        # 결과 저장
        print(f"💾 결과 저장: {output_path}")
        
        if file_format == "text":
            # 텍스트 파일로 저장 (마스킹된 텍스트만)
            df_masked.select("masked_text").write.mode("overwrite").text(output_path)
            
        elif file_format == "csv":
            # CSV 파일로 저장 (원본 + 마스킹 결과)
            df_masked.write.mode("overwrite").option("header", "true").csv(output_path)
            
        elif file_format == "json":
            # JSON 파일로 저장
            df_masked.write.mode("overwrite").json(output_path)
        
        # 통계 정보
        total_records = df_masked.count()
        print(f"✅ 처리 완료: {total_records}개 레코드")
        
        # 샘플 결과 출력
        print("\n📄 마스킹 결과 샘플:")
        df_masked.select(text_column, "masked_text").limit(3).show(truncate=False)
        
        return df_masked
        
    except Exception as e:
        print(f"❌ 파일 처리 실패: {e}")
        raise

def process_multiple_file_directories(base_input_path, base_output_path, directories, file_format="text"):
    """여러 디렉토리의 파일들을 배치 처리"""
    
    results = {}
    
    for directory in directories:
        input_path = f"{base_input_path}/{directory}"
        output_path = f"{base_output_path}/{directory}_masked"
        
        print(f"\n📁 디렉토리 처리: {directory}")
        
        try:
            df_result = process_text_files_from_dbfs(input_path, output_path, file_format)
            results[directory] = {
                'status': 'success',
                'record_count': df_result.count(),
                'output_path': output_path
            }
        except Exception as e:
            print(f"❌ {directory} 처리 실패: {e}")
            results[directory] = {
                'status': 'failed',
                'error': str(e)
            }
    
    # 배치 처리 결과 요약
    print("\n🎉 배치 처리 결과 요약:")
    print("=" * 50)
    
    success_count = 0
    total_records = 0
    
    for directory, result in results.items():
        if result['status'] == 'success':
            success_count += 1
            total_records += result['record_count']
            print(f"✅ {directory}: {result['record_count']}개 레코드 처리 완료")
        else:
            print(f"❌ {directory}: 처리 실패 - {result['error']}")
    
    print(f"\n📊 전체 결과:")
    print(f"성공: {success_count}/{len(directories)} 디렉토리")
    print(f"총 처리 레코드: {total_records:,}개")
    
    return results

def main_databricks_processing(srcDir=None, tgtDir=None, file_format="text", directories=None):
    """메인 Databricks 파일 처리 함수"""
    
    print("🔒 Databricks GLiNER 파일 마스킹 도구")
    print("=" * 60)
    
    # 기본 디렉토리 설정
    if srcDir is None:
        srcDir = "/dbfs/FileStore/shared_uploads/input/"
        print(f"📂 기본 소스 디렉토리 사용: {srcDir}")
    
    if tgtDir is None:
        tgtDir = "/dbfs/FileStore/shared_uploads/output/"
        print(f"📁 기본 타겟 디렉토리 사용: {tgtDir}")
    
    print(f"📂 소스 디렉토리: {srcDir}")
    print(f"📁 타겟 디렉토리: {tgtDir}")
    print(f"📄 파일 형식: {file_format}")
    
    # 디렉토리 존재 확인 및 생성
    try:
        dbutils.fs.ls(srcDir)
        print("✅ 소스 디렉토리 존재 확인")
    except:
        print(f"⚠️ 소스 디렉토리가 존재하지 않습니다: {srcDir}")
        print("🧪 데모용 데이터 생성...")
        
        # 데모용 데이터 생성
        demo_data = [
            (1, "홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 2025년 6월에 1달간 병원에 있었어요."),
            (2, "김철수(010-1234-5678)는 부산대학교병원에서 고혈압 진료를 받았습니다."),
            (3, "이영희님의 주민번호는 123456-1234567이고, 이메일은 test@example.com입니다."),
            (4, "박민수 환자가 현대자동차에 다니며, 서울시 종로구 세종대로 123번지에 살고 있습니다."),
            (5, "정수진(35세)은 당뇨병으로 인슐린을 투약 중이며, 연봉은 5000만원입니다.")
        ]
        
        # DataFrame 생성 및 임시 파일로 저장
        df_demo = spark.createDataFrame(demo_data, ["line_id", "text"])
        
        # 데모 파일 저장
        demo_srcDir = srcDir + "demo/"
        df_demo.write.mode("overwrite").option("header", "true").csv(demo_srcDir)
        print(f"✅ 데모 데이터 생성됨: {demo_srcDir}")
        
        # 데모 데이터로 처리
        srcDir = demo_srcDir
    
    # 처리 방식 선택
    if directories is not None:
        # 여러 디렉토리 배치 처리
        print(f"📁 배치 처리 모드: {len(directories)}개 디렉토리")
        results = process_multiple_file_directories(srcDir, tgtDir, directories, file_format)
        
        return {
            'mode': 'batch',
            'srcDir': srcDir,
            'tgtDir': tgtDir,
            'directories': directories,
            'results': results,
            'file_format': file_format
        }
    
    else:
        # 단일 디렉토리 처리
        print("📄 단일 디렉토리 처리 모드")
        df_result = process_text_files_from_dbfs(srcDir, tgtDir, file_format)
        
        return {
            'mode': 'single',
            'srcDir': srcDir,
            'tgtDir': tgtDir,
            'record_count': df_result.count(),
            'file_format': file_format,
            'dataframe': df_result
        }

def setup_databricks_directories(base_path="/dbfs/FileStore/shared_uploads/"):
    """Databricks 디렉토리 설정 도우미 함수"""
    
    print("🔧 Databricks 디렉토리 설정")
    print("=" * 40)
    
    # 기본 디렉토리 구조 생성
    directories = {
        'input': base_path + "pii_masking/input/",
        'output': base_path + "pii_masking/output/",
        'archive': base_path + "pii_masking/archive/",
        'logs': base_path + "pii_masking/logs/"
    }
    
    for name, path in directories.items():
        try:
            dbutils.fs.mkdirs(path)
            print(f"✅ {name} 디렉토리: {path}")
        except Exception as e:
            print(f"⚠️ {name} 디렉토리 생성 실패: {e}")
    
    print("\n📝 사용 예시:")
    print(f"srcDir = '{directories['input']}'")
    print(f"tgtDir = '{directories['output']}'")
    
    return directories

# 위젯을 통한 매개변수 입력 (Databricks 노트북용)
def create_databricks_widgets():
    """Databricks 노트북 위젯 생성"""
    
    try:
        # 위젯 생성
        dbutils.widgets.text("srcDir", "/dbfs/FileStore/shared_uploads/pii_masking/input/", "소스 디렉토리")
        dbutils.widgets.text("tgtDir", "/dbfs/FileStore/shared_uploads/pii_masking/output/", "타겟 디렉토리")
        dbutils.widgets.dropdown("file_format", "text", ["text", "csv", "json"], "파일 형식")
        dbutils.widgets.text("directories", "", "배치 디렉토리 (쉼표 구분, 선택사항)")
        
        # 위젯 값 가져오기
        srcDir = dbutils.widgets.get("srcDir")
        tgtDir = dbutils.widgets.get("tgtDir")
        file_format = dbutils.widgets.get("file_format")
        directories_str = dbutils.widgets.get("directories")
        
        directories = None
        if directories_str.strip():
            directories = [d.strip() for d in directories_str.split(",")]
        
        print("🎛️ 위젯 매개변수:")
        print(f"  srcDir: {srcDir}")
        print(f"  tgtDir: {tgtDir}")
        print(f"  file_format: {file_format}")
        print(f"  directories: {directories}")
        
        return srcDir, tgtDir, file_format, directories
        
    except Exception as e:
        print(f"⚠️ 위젯 생성 실패 (노트북 환경이 아닐 수 있음): {e}")
        return None, None, "text", None

# 스크립트 실행
if __name__ == "__main__":
    print("🚀 Databricks GLiNER 개인정보 마스킹 시작")
    print("=" * 50)
    
    # 실행 방법 선택
    execution_mode = input("실행 방법을 선택하세요 (1: 위젯, 2: 직접입력, 3: 데모): ").strip()
    
    if execution_mode == "1":
        # 위젯 사용
        print("🎛️ Databricks 위젯 생성...")
        srcDir, tgtDir, file_format, directories = create_databricks_widgets()
        
        if srcDir is not None:
            result = main_databricks_processing(srcDir, tgtDir, file_format, directories)
        else:
            print("❌ 위젯 생성 실패, 데모 모드로 실행")
            result = main_databricks_processing()
    
    elif execution_mode == "2":
        # 직접 입력
        print("📝 매개변수 직접 입력:")
        srcDir = input("소스 디렉토리: ").strip()
        tgtDir = input("타겟 디렉토리: ").strip()
        file_format = input("파일 형식 (text/csv/json): ").strip() or "text"
        directories_str = input("배치 디렉토리 (쉼표 구분, 선택사항): ").strip()
        
        directories = None
        if directories_str:
            directories = [d.strip() for d in directories_str.split(",")]
        
        result = main_databricks_processing(srcDir, tgtDir, file_format, directories)
    
    else:
        # 데모 모드
        print("🧪 데모 모드 실행...")
        
        # 디렉토리 설정
        dirs = setup_databricks_directories()
        
        result = main_databricks_processing(
            srcDir=dirs['input'],
            tgtDir=dirs['output'],
            file_format="csv"
        )
    
    # 결과 출력
    print(f"\n🎉 처리 완료!")
    print(f"📊 결과 요약:")
    print(f"  - 모드: {result['mode']}")
    print(f"  - 소스: {result['srcDir']}")
    print(f"  - 타겟: {result['tgtDir']}")
    print(f"  - 파일 형식: {result['file_format']}")
    
    if result['mode'] == 'single':
        print(f"  - 처리 레코드: {result['record_count']:,}개")
    else:
        success_count = sum(1 for r in result['results'].values() if r['status'] == 'success')
        total_dirs = len(result['directories'])
        print(f"  - 성공 디렉토리: {success_count}/{total_dirs}")
    
    print("\n💡 추가 사용 팁:")
    print("1. 대용량 파일 처리 시 파티션 수 조정: df.repartition(200)")
    print("2. 메모리 최적화: spark.conf.set('spark.sql.adaptive.enabled', 'true')")
    print("3. 결과 저장 형식: .csv(), .json(), .parquet() 등 선택 가능")
    print("4. 배치 크기 조정: spark.conf.set('spark.sql.execution.arrow.maxRecordsPerBatch', '1000')")
    print("5. 위젯 제거: dbutils.widgets.removeAll()")

# Spark 세션 종료 (필요시)
# spark.stop()
