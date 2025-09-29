
# 🔒 한국어 개인정보 마스킹 도구 모음

다양한 방식으로 한국어 텍스트의 개인정보를 마스킹하는 Python 도구들입니다.

## 📋 목차
- [파일 구성](#파일-구성)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [성능 비교](#성능-비교)
- [권장사항](#권장사항)

## 📁 파일 구성

### 🤖 **AI 모델 기반**

#### `ModelBaseMasking.py` ⭐⭐⭐⭐⭐
- **설명**: GLiNER 모델을 사용한 고정밀 개인정보 마스킹
- **특징**: 
  - 35개 엔티티 타입 지원 (PERSON, PHONE, EMAIL, MEDICAL 등)
  - 부분 마스킹 (홍길동 → 홍*동, 010-1234-5678 → 010-1234-****)
  - 싱글톤 패턴으로 메모리 효율성 개선
  - 배치 처리 지원
- **장점**: 높은 정확도, 다양한 개인정보 유형 감지
- **단점**: 모델 다운로드 필요 (1.2GB), 초기 로딩 시간
- **적합한 용도**: 정확도가 중요한 프로덕션 환경

```python
from ModelBaseMasking import model_based_partial_masking

text = "홍길동(010-1234-5678)은 서울 강남구에 거주합니다."
masked_text, items = model_based_partial_masking(text)
print(masked_text)  # 홍*동(010-1234-****)은 서* 강*구에 거주합니다.
```

#### `ModelBaseAsUDF.py` ⭐⭐⭐⭐
- **설명**: Databricks/Spark 환경용 GLiNER 기반 UDF
- **특징**:
  - PySpark UDF로 분산 처리 지원
  - 싱글톤 패턴으로 클러스터 내 모델 공유
  - pandas_udf와 일반 UDF 두 가지 방식 제공
  - 정규식 백업 시스템
- **장점**: 대용량 데이터 처리, 분산 환경 최적화
- **단점**: Spark 환경 필요, 복잡한 설정
- **적합한 용도**: 빅데이터 환경, Databricks

```python
# Databricks/Spark 환경에서
df_masked = df.withColumn("masked_text", gliner_mask_udf(col("text")))
```

### 🔍 **spaCy 기반**

#### `spacyRulePatialMasking.py` ⭐⭐⭐⭐
- **설명**: spaCy NER + 정규식을 결합한 부분 마스킹
- **특징**:
  - 가벼운 spaCy 모델 사용 (14.7MB)
  - 부분 마스킹 지원
  - 한국어 특화 정규식 패턴 보완
  - 실시간 처리 가능
- **장점**: 빠른 속도, 안정성, 적당한 정확도
- **단점**: GLiNER 대비 낮은 정확도
- **적합한 용도**: 실시간 처리, 리소스 제한 환경

```python
from spacyRulePatialMasking import final_masking

text = "홍길동(010-1234-5678)은 당뇨병 치료 중입니다."
masked_text, items = final_masking(text)
print(masked_text)  # 홍*동(010-1234-****)은 당*병 치료 중입니다.
```

#### `spacyRuleFullMasking.py.py` ⭐⭐⭐
- **설명**: spaCy 기반 완전 마스킹 (태그 치환)
- **특징**:
  - 개인정보를 [PERSON], [ORGANIZATION] 등 태그로 치환
  - spaCy + 정규식 하이브리드 방식
- **장점**: 빠른 처리, 명확한 구분
- **단점**: 가독성 저하, 부분 정보 손실
- **적합한 용도**: 완전 익명화가 필요한 경우

### 📝 **정규식 기반**

#### `RuleBaseMasking.py` ⭐⭐⭐
- **설명**: 순수 정규식 패턴 기반 마스킹
- **특징**:
  - 외부 라이브러리 의존성 없음
  - 빠른 처리 속도
  - 한국어 특화 패턴
  - 완전 마스킹 방식
- **장점**: 초경량, 빠른 속도, 의존성 없음
- **단점**: 낮은 정확도, 제한적 패턴
- **적합한 용도**: 간단한 전처리, 프로토타이핑

```python
from RuleBaseMasking import simple_masking

text = "홍길동은 서울 강남구에서 삼성병원에 다닙니다."
masked_text = simple_masking(text)
print(masked_text)  # [PERSON]은 [LOCATION]에서 [ORGANIZATION]에 다닙니다.
```

### 📚 **참고 자료**

#### `singleton_examples.py`
- **설명**: 싱글톤 패턴 구현 방법들의 예제 모음
- **포함 내용**:
  - 전역 변수 방식
  - 클래스 기반 싱글톤
  - 데코레이터 방식
  - 모듈 레벨 싱글톤
- **용도**: 학습 자료, 패턴 참고

## 🚀 설치 방법

<details>
<summary><strong>📦 기본 설치 (클릭하여 펼치기)</strong></summary>

### 온라인 환경 (일반적인 경우)
```bash
# 가상환경 생성 (권장)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 기본 패키지
pip install pandas numpy
```

</details>

<details>
<summary><strong>🔒 폐쇄망 환경 (오프라인 설치)</strong></summary>

**방법 1: 자동 스크립트 사용 (권장)**
```bash
# 1. 온라인 환경에서 오프라인 패키지 생성
python offline_setup.py

# 2. 생성된 offline_packages 폴더를 폐쇄망으로 복사
# USB, 내부망 파일서버 등을 통해 전송

# 3. 폐쇄망에서 설치 스크립트 실행
# Windows:
cd offline_packages
scripts\install_windows.bat

# Linux/Mac:
cd offline_packages
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
```

**방법 2: 수동 설치**

*1단계: 온라인 환경에서 패키지 다운로드*
```bash
# 다운로드용 디렉토리 생성
mkdir offline_packages
cd offline_packages

# 기본 패키지 다운로드
pip download pandas numpy regex tqdm requests

# GLiNER 관련 패키지 다운로드 (ModelBaseMasking.py용)
pip download gliner torch transformers huggingface_hub safetensors tokenizers

# spaCy 관련 패키지 다운로드
pip download spacy spacy-legacy spacy-loggers murmurhash cymem preshed thinc wasabi srsly catalogue

# spaCy 한국어 모델 다운로드
wget https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.8.0/ko_core_news_sm-3.8.0-py3-none-any.whl

# Databricks용 추가 패키지
pip download pyspark py4j pyarrow

# 한국어 형태소 분석기 (선택사항)
pip download konlpy eunjeon soynlp
```

*2단계: GLiNER 모델 수동 다운로드*
```bash
# https://huggingface.co/taeminlee/gliner_ko 접속
# "Files and versions" 탭에서 다음 파일들 다운로드:
# - config.json
# - pytorch_model.bin (1.21GB)
# - tokenizer_config.json
# - vocab.txt
# - special_tokens_map.json
```

*3단계: 폐쇄망으로 파일 전송*
```bash
# offline_packages 폴더 전체를 폐쇄망으로 복사
# USB, 내부망 파일서버 등을 통해 전송
```

*4단계: 폐쇄망에서 오프라인 설치*
```bash
# 가상환경 생성
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 기본 패키지 설치
pip install --no-index --find-links ./offline_packages pandas numpy regex tqdm requests

# GLiNER 설치
pip install --no-index --find-links ./offline_packages torch transformers huggingface_hub safetensors tokenizers gliner

# spaCy 설치
pip install --no-index --find-links ./offline_packages spacy spacy-legacy spacy-loggers murmurhash cymem preshed thinc wasabi srsly catalogue
pip install --no-index --find-links ./offline_packages ko_core_news_sm-3.8.0-py3-none-any.whl

# GLiNER 모델 파일 복사
# Windows: %USERPROFILE%\.cache\huggingface\hub\models--taeminlee--gliner_ko\
# Linux/Mac: ~/.cache/huggingface/hub/models--taeminlee--gliner_ko/
mkdir -p ~/.cache/huggingface/hub/models--taeminlee--gliner_ko/
cp downloaded_model_files/* ~/.cache/huggingface/hub/models--taeminlee--gliner_ko/
```

</details>

<details>
<summary><strong>🤖 GLiNER 모델 기반 (ModelBaseMasking.py)</strong></summary>

#### 온라인 설치
```bash
pip install gliner torch transformers
```

#### 🔒 폐쇄망 오프라인 설치
```bash
# 1. 온라인 환경에서 다운로드
mkdir gliner_offline
pip download --dest gliner_offline gliner torch transformers huggingface_hub safetensors tokenizers

# 2. GLiNER 모델 수동 다운로드 (1번의 Download가 가능한 경우 불필요)
# https://huggingface.co/taeminlee/gliner_ko 접속
# "Files and versions" 탭에서 다음 파일들 다운로드:
# - config.json
# - pytorch_model.bin (1.21GB)
# - tokenizer_config.json
# - vocab.txt

# 3. 폐쇄망에서 설치 : 다운로드 경로 지정필요
pip install --no-index --find-links ./gliner_offline gliner torch transformers

# 4. 모델 파일을 캐시 디렉토리에 복사
# Windows: %USERPROFILE%\.cache\huggingface\hub\models--taeminlee--gliner_ko
# Linux/Mac: ~/.cache/huggingface/hub/models--taeminlee--gliner_ko
mkdir -p ~/.cache/huggingface/hub/models--taeminlee--gliner_ko
cp downloaded_model_files/* ~/.cache/huggingface/hub/models--taeminlee--gliner_ko/
```

</details>

<details>
<summary><strong>⚡ Databricks/Spark 환경 (ModelBaseAsUDF.py)</strong></summary>

**방법 1: KoNLPy (권장 - 가장 안정적)**
```bash
pip install konlpy

# Windows 추가 설정
# 1. Java 8+ 설치 필요 (https://www.oracle.com/java/technologies/downloads/)
# 2. JAVA_HOME 환경변수 설정

# 설치 확인
python -c "from konlpy.tag import Okt; print('KoNLPy 설치 완료!')"
```

**방법 2: MeCab-ko (고성능)**
```bash
# Windows (복잡함 - 고급 사용자용)
pip install mecab-python3

# 추가로 MeCab-ko 바이너리 설치 필요:
# 1. https://github.com/Pusnow/mecab-ko-msvc/releases 에서 다운로드
# 2. 압축 해제 후 PATH 환경변수에 추가
# 3. mecab-ko-dic 사전 설치

# Linux/Mac (더 쉬움)
# Ubuntu/Debian:
sudo apt-get install mecab mecab-ko mecab-ko-dic
pip install mecab-python3

# macOS:
brew install mecab mecab-ko mecab-ko-dic
pip install mecab-python3
```

**방법 3: eunjeon (간단한 대안)**
```bash
pip install eunjeon
# Java 의존성 없음, Windows에서 설치 쉬움
```

**방법 4: soynlp (순수 Python)**
```bash
pip install soynlp
# 의존성 없음, 가장 설치 쉬움
```

</details>

<details>
<summary><strong>🔍 spaCy 기반</strong></summary>

#### 온라인 설치
```bash
pip install spacy

# 한국어 모델 다운로드
python -m spacy download ko_core_news_sm

# 다운로드 확인
python -c "import spacy; nlp = spacy.load('ko_core_news_sm'); print('spaCy 한국어 모델 로드 완료!')"
```

#### 🔒 폐쇄망 오프라인 설치
```bash
# 1. 온라인 환경에서 다운로드
mkdir spacy_offline

# spaCy 패키지 다운로드
pip download --dest spacy_offline spacy

# 한국어 모델 직접 다운로드
wget https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.8.0/ko_core_news_sm-3.8.0-py3-none-any.whl -P spacy_offline/

# 2. 폐쇄망에서 설치
pip install --no-index --find-links ./spacy_offline spacy
pip install --no-index --find-links ./spacy_offline ko_core_news_sm-3.8.0-py3-none-any.whl

# 3. 설치 확인
python -c "import spacy; nlp = spacy.load('ko_core_news_sm'); print('spaCy 오프라인 설치 완료!')"
```

</details>

<details>
<summary><strong>⚠️ spaCy 모델 다운로드 문제 해결</strong></summary>

**spaCy 모델 다운로드 문제 해결:**
```bash
# 방법 1: 직접 다운로드 (네트워크 문제 시)
pip install https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.8.0/ko_core_news_sm-3.8.0-py3-none-any.whl

# 방법 2: 캐시 클리어 후 재시도
pip cache purge
python -m spacy download ko_core_news_sm

# 방법 3: 수동 설치
# 1. https://github.com/explosion/spacy-models/releases 에서 ko_core_news_sm 다운로드
# 2. pip install [다운로드한_파일.whl]
```

### Databricks/Spark 환경 (ModelBaseAsUDF.py)

#### 온라인 설치
```bash
pip install pyspark gliner torch transformers
```

#### 🔒 폐쇄망 Databricks 설치

**방법 1: 오프라인 패키지 업로드**
```bash
# 1. 온라인 환경에서 패키지 다운로드
mkdir databricks_offline
pip download --dest databricks_offline pyspark gliner torch transformers huggingface_hub

# 2. Databricks DBFS에 업로드
# Databricks 워크스페이스 → Data → DBFS → Upload
# databricks_offline 폴더를 /FileStore/offline_packages/로 업로드

# 3. 클러스터에서 설치
%pip install --no-index --find-links /dbfs/FileStore/offline_packages/ gliner torch transformers
```

**방법 2: Wheel 파일 직접 업로드**
```bash
# 1. 온라인에서 wheel 파일들 다운로드
pip download --only-binary=:all: gliner torch transformers

# 2. Databricks 클러스터 라이브러리에 직접 업로드
# 클러스터 → Libraries → Install New → Upload → Python Whl
# 각 .whl 파일을 개별적으로 업로드
```

**Databricks 클러스터 설정:**
1. **온라인 환경 클러스터 라이브러리 설치**:
   - Databricks 워크스페이스 → 클러스터 → Libraries → Install New
   - PyPI에서 `gliner`, `torch`, `transformers` 설치

2. **폐쇄망 환경 클러스터 라이브러리 설치**:
   - 클러스터 → Libraries → Install New → Upload
   - 미리 다운로드한 .whl 파일들을 업로드

</details>

<details>
<summary><strong>🔧 Databricks 클러스터 설정</strong></summary>

**클러스터 설정 권장사항:**
   ```
   Driver: Standard_DS3_v2 (4 cores, 14GB RAM) 이상
   Workers: Standard_DS3_v2 (4 cores, 14GB RAM) 이상
   Min Workers: 2, Max Workers: 8
   ```

3. **환경변수 설정** (선택사항):
   ```bash
   # Spark 설정에서 환경변수 추가
   HF_HOME=/dbfs/tmp/huggingface_cache
   TRANSFORMERS_CACHE=/dbfs/tmp/transformers_cache
   ```

**Azure Databricks 특별 설정:**
```python
# 노트북 셀에서 실행
%pip install gliner torch transformers

# 클러스터 재시작 후
dbutils.library.restartPython()
```

</details>

<details>
<summary><strong>💰 Databricks 비용 계산 (한국 기준)</strong></summary>

### DBU 소모량 예상치

**클러스터 구성별 시간당 DBU:**
- **Standard_DS3_v2** (4 cores, 14GB): 0.75 DBU/시간
- **Standard_DS4_v2** (8 cores, 28GB): 1.5 DBU/시간  
- **Standard_DS5_v2** (16 cores, 56GB): 3.0 DBU/시간

**처리량별 예상 비용 (1000라인 파일 기준, 2024년 한국):**

| 파일 수 | 총 라인 수 | 처리 시간 | 클러스터 | DBU 소모 | 예상 비용 (₩) |
|---------|------------|-----------|----------|----------|---------------|
| **10개 파일** | 10,000 라인 | ~15분 | DS3_v2 (2 workers) | 0.75 DBU | ₩1,125 |
| **100개 파일** | 100,000 라인 | ~2시간 | DS3_v2 (4 workers) | 6 DBU | ₩9,000 |
| **1,000개 파일** | 1,000,000 라인 | ~12시간 | DS4_v2 (6 workers) | 54 DBU | ₩81,000 |
| **10,000개 파일** | 10,000,000 라인 | ~5일 | DS5_v2 (8 workers) | 360 DBU | ₩540,000 |

**비용 계산 기준:**
- **DBU 단가**: ₩1,500/DBU (Azure Databricks Premium, 한국 중부 리전)
- **처리 속도**: 라인당 평균 0.04초 (GLiNER 모델, 평균 텍스트 길이 50자 기준)
- **파일 크기**: 1000라인 × 평균 50자 = 약 50KB/파일
- **클러스터 효율**: 75% (모델 로딩, I/O 오버헤드, 파일 처리 지연 고려)

### 비용 최적화 팁

**1. 클러스터 크기 최적화**
```python
# 소규모 데이터 (< 10,000개): 작은 클러스터
cluster_config = {
    "driver": "Standard_DS3_v2",
    "workers": "Standard_DS3_v2", 
    "min_workers": 2,
    "max_workers": 4
}

# 대규모 데이터 (> 100,000개): 큰 클러스터로 빠른 처리
cluster_config = {
    "driver": "Standard_DS4_v2",
    "workers": "Standard_DS4_v2",
    "min_workers": 4, 
    "max_workers": 8
}
```

**2. 자동 종료 설정**
```python
# 클러스터 자동 종료 (유휴 시간 10분)
cluster_config["autotermination_minutes"] = 10
```

**3. 스팟 인스턴스 활용**
```python
# 스팟 인스턴스로 최대 90% 비용 절감
cluster_config["aws_attributes"] = {
    "first_on_demand": 1,
    "availability": "SPOT_WITH_FALLBACK",
    "spot_bid_price_percent": 50
}
```

**4. 배치 크기 최적화**
```python
# 배치 크기 조정으로 처리 효율 향상
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "1000")
df = df.repartition(200)  # 파티션 수 최적화
```

### 실제 비용 예시 (월간 처리량 기준)

**시나리오 1: 소규모 스타트업 (콜센터)**
- 월 500개 파일 (50만 라인) 처리
- 주 2회 배치 처리 (회당 125개 파일)
- 클러스터: DS3_v2 (4 workers)
- **예상 월 비용: ₩40,500**

**시나리오 2: 중간 규모 기업 (고객지원)**  
- 월 2,000개 파일 (200만 라인) 처리
- 일 1회 배치 처리 (회당 67개 파일)
- 클러스터: DS4_v2 (6 workers)
- **예상 월 비용: ₩162,000**

**시나리오 3: 대기업 (금융/통신)**
- 월 10,000개 파일 (1,000만 라인) 처리  
- 일 2회 배치 처리 (회당 167개 파일)
- 클러스터: DS5_v2 (8 workers)
- **예상 월 비용: ₩540,000**

**시나리오 4: 대형 플랫폼 (소셜미디어/이커머스)**
- 월 50,000개 파일 (5,000만 라인) 처리
- 실시간 스트리밍 처리
- 클러스터: DS5_v2 (12 workers) 상시 운영
- **예상 월 비용: ₩2,700,000**

**💡 비용 절감 권장사항:**
1. **개발/테스트**: 로컬 환경에서 `ModelBaseMasking.py` 사용
2. **소규모 배치**: `spacyRulePatialMasking.py`로 비용 절감
3. **대규모만**: Databricks `ModelBaseAsUDF.py` 사용
4. **하이브리드**: 민감도에 따라 도구 선택적 사용

## 🔧 설치 문제 해결

<details>
<summary><strong>⚠️ 자주 발생하는 문제들</strong></summary>

#### 1. GLiNER 모델 다운로드 실패
```bash
# 문제: 네트워크 타임아웃, 방화벽 차단
# 해결: 수동 다운로드 후 캐시 디렉토리에 복사

# 모델 캐시 위치 확인
python -c "from transformers import GLiNER; print(GLiNER.cache_dir)"

# 또는 환경변수로 캐시 디렉토리 지정
export HF_HOME=/path/to/cache  # Linux/Mac
set HF_HOME=C:\path\to\cache   # Windows
```

#### 2. Java 관련 오류 (KoNLPy 사용 시)
```bash
# 오류: "Java gateway process exited before sending its port number"
# 해결 방법:

# Windows:
# 1. Oracle JDK 8+ 설치 (https://www.oracle.com/java/technologies/downloads/)
# 2. 환경변수 설정:
#    JAVA_HOME=C:\Program Files\Java\jdk-11.0.x
#    PATH에 %JAVA_HOME%\bin 추가

# 설치 확인:
java -version
python -c "from konlpy.tag import Okt; print('성공!')"
```

#### 3. MeCab 설치 오류 (Windows)
```bash
# 오류: "The MeCab dictionary path is empty"
# 해결: 더 간단한 대안 사용

# 대신 eunjeon 사용 (권장):
pip uninstall mecab-python3
pip install eunjeon

# 또는 KoNLPy의 Okt 사용:
pip install konlpy
# Java 설치 후 사용
```

#### 4. spaCy 모델 다운로드 실패
```bash
# 오류: "Can't find model 'ko_core_news_sm'"
# 해결 방법들:

# 방법 1: 프록시 설정
pip install --proxy http://proxy.company.com:8080 spacy
python -m spacy download ko_core_news_sm --proxy http://proxy.company.com:8080

# 방법 2: 직접 URL로 설치
pip install https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.8.0/ko_core_news_sm-3.8.0-py3-none-any.whl

# 방법 3: 오프라인 설치
# 1. 다른 컴퓨터에서 모델 다운로드
# 2. .whl 파일을 USB로 복사
# 3. pip install ko_core_news_sm-3.8.0-py3-none-any.whl
```

### 설치 확인 스크립트

각 도구별 설치 상태를 확인하는 스크립트:

```python
# install_check.py
def check_installations():
    """설치 상태 확인"""
    results = {}
    
    # 1. 기본 패키지
    try:
        import re, pandas, numpy
        results['기본 패키지'] = '✅ 설치됨'
    except ImportError as e:
        results['기본 패키지'] = f'❌ 누락: {e}'
    
    # 2. GLiNER
    try:
        from gliner import GLiNER
        results['GLiNER'] = '✅ 설치됨'
    except ImportError:
        results['GLiNER'] = '❌ 누락: pip install gliner'
    
    # 3. spaCy + 한국어 모델
    try:
        import spacy
        nlp = spacy.load('ko_core_news_sm')
        results['spaCy'] = '✅ 설치됨 (한국어 모델 포함)'
    except ImportError:
        results['spaCy'] = '❌ 누락: pip install spacy'
    except OSError:
        results['spaCy'] = '⚠️ spaCy 설치됨, 한국어 모델 누락'
    
    # 4. 형태소 분석기들
    morphology_tools = []
    
    try:
        from konlpy.tag import Okt
        Okt()
        morphology_tools.append('KoNLPy')
    except:
        pass
    
    try:
        import mecab
        morphology_tools.append('MeCab')
    except:
        pass
    
    try:
        import eunjeon
        morphology_tools.append('eunjeon')
    except:
        pass
    
    try:
        import soynlp
        morphology_tools.append('soynlp')
    except:
        pass
    
    if morphology_tools:
        results['형태소 분석기'] = f'✅ {", ".join(morphology_tools)}'
    else:
        results['형태소 분석기'] = '⚠️ 없음 (선택사항)'
    
    # 5. Spark (UDF용)
    try:
        import pyspark
        results['PySpark'] = '✅ 설치됨'
    except ImportError:
        results['PySpark'] = '❌ 누락 (UDF 사용 시 필요)'
    
    # 결과 출력
    print("🔍 설치 상태 확인 결과:")
    print("=" * 50)
    for tool, status in results.items():
        print(f"{tool:15} : {status}")
    
    print("\n💡 권장 최소 설치:")
    print("pip install pandas numpy spacy")
    print("python -m spacy download ko_core_news_sm")

if __name__ == "__main__":
    check_installations()
```

## 💡 사용 방법

<details>
<summary><strong>🧪 간단한 테스트</strong></summary>
```python
# 정규식 기반 (가장 간단)
from RuleBaseMasking import simple_masking
result = simple_masking("홍길동은 서울에 살고 있습니다.")

# spaCy 기반 (균형잡힌 선택)
from spacyRulePatialMasking import final_masking
result, items = final_masking("홍길동(010-1234-5678)입니다.")

# GLiNER 기반 (최고 정확도)
from ModelBaseMasking import model_based_partial_masking
result, items = model_based_partial_masking("홍길동의 이메일은 test@example.com입니다.")
```

### 2. 배치 처리
```python
# ModelBaseMasking.py의 배치 처리 기능 활용
texts = ["텍스트1", "텍스트2", "텍스트3"]
results = batch_masking(texts, batch_size=10)
```

### 3. Databricks 환경
```python
# ModelBaseAsUDF.py 사용
from pyspark.sql.functions import col
df_masked = df.withColumn("masked_text", gliner_mask_udf(col("text")))
```

</details>

## 📊 성능 비교

<details>
<summary><strong>📈 도구별 성능 비교표</strong></summary>

| 도구 | 정확도 | 속도 | 메모리 | 의존성 | 설치 복잡도 |
|------|--------|------|--------|--------|-------------|
| **ModelBaseMasking.py** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 높음 | 중간 |
| **spacyRulePatialMasking.py** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 중간 | 쉬움 |
| **RuleBaseMasking.py** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 없음 | 매우 쉬움 |
| **ModelBaseAsUDF.py** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 매우 높음 | 어려움 |

### 처리량 비교 (1000개 텍스트 기준)
- **RuleBaseMasking.py**: ~1초
- **spacyRulePatialMasking.py**: ~5초
- **ModelBaseMasking.py**: ~30초 (첫 실행), ~10초 (이후)
- **ModelBaseAsUDF.py**: ~5초 (분산 환경)

</details>

## 🎯 권장사항

<details>
<summary><strong>📈 데이터 규모별 선택 가이드</strong></summary>

### 📈 **데이터 규모별 선택 (비용 고려)**

#### 소규모 (< 100개 파일) - 비용: 무료~₩9,000
```
RuleBaseMasking.py (무료) → spacyRulePatialMasking.py (무료) → ModelBaseMasking.py (무료)
```
**권장**: 로컬 환경에서 무료 도구 사용 (100개 파일 = 10만 라인)

#### 중간 규모 (100 ~ 2,000개 파일) - 비용: ₩9,000~₩162,000  
```
spacyRulePatialMasking.py (무료) → ModelBaseMasking.py (무료) → ModelBaseAsUDF.py (유료)
```
**권장**: 정확도가 중요하면 Databricks, 비용이 중요하면 로컬 처리

#### 대규모 (2,000개+ 파일) - 비용: ₩162,000~₩540,000+
```
ModelBaseAsUDF.py (Databricks/Spark 환경) - 필수
```
**권장**: 분산 처리 필수, 스팟 인스턴스로 비용 절감

### 🎨 **용도별 선택 (비용 효율성 고려)**

#### 프로토타이핑 / 빠른 테스트
- **추천**: `RuleBaseMasking.py`
- **이유**: 의존성 없음, 즉시 실행 가능, **무료**
- **비용**: ₩0

#### 실시간 서비스 (< 1만 요청/일)
- **추천**: `spacyRulePatialMasking.py`
- **이유**: 속도와 정확도의 균형, **무료**
- **비용**: ₩0 (로컬 서버 운영비만)

#### 고정밀 배치 처리 (정확도 우선)
- **추천**: `ModelBaseMasking.py` (로컬) 또는 `ModelBaseAsUDF.py` (대용량)
- **이유**: 최고 정확도, 다양한 개인정보 유형
- **비용**: ₩0 (로컬) / ₩9,000~₩162,000 (Databricks, 파일 수에 따라)

#### 빅데이터 환경 (2,000개+ 파일 처리)
- **추천**: `ModelBaseAsUDF.py`
- **이유**: 분산 처리 필수, 확장성
- **비용**: ₩162,000~₩2,700,000+ (월간 처리 기준, 파일 수에 따라)

#### 비용 최적화 전략
- **개발 단계**: 로컬 도구로 개발 (`ModelBaseMasking.py`)
- **테스트 단계**: 소량 데이터로 Databricks 테스트
- **운영 단계**: 데이터 규모에 따라 선택적 사용

</details>

<details>
<summary><strong>🔧 마스킹 방식별 선택</strong></summary>

#### 부분 마스킹 (홍길동 → 홍*동)
- `ModelBaseMasking.py`
- `spacyRulePatialMasking.py`

#### 완전 마스킹 ([PERSON])
- `RuleBaseMasking.py`
- `spacyRuleFullMasking.py.py`

</details>

<details>
<summary><strong>⚠️ 주의사항 및 시스템 요구사항</strong></summary>

### 시스템 요구사항
- **Python**: 3.8 이상
- **메모리**: 
  - GLiNER 기반: 최소 4GB RAM (권장 8GB)
  - spaCy 기반: 최소 2GB RAM
  - 정규식 기반: 1GB RAM
- **저장공간**: 
  - GLiNER 모델: 1.2GB
  - spaCy 한국어 모델: 15MB
- **네트워크**: 초기 모델 다운로드 시 필요

### 운영체제별 호환성
| 도구 | Windows | Linux | macOS |
|------|---------|-------|-------|
| **RuleBaseMasking.py** | ✅ | ✅ | ✅ |
| **spacyRulePatialMasking.py** | ✅ | ✅ | ✅ |
| **ModelBaseMasking.py** | ✅ | ✅ | ✅ |
| **ModelBaseAsUDF.py** | ✅ | ✅ | ✅ |
| **KoNLPy (형태소 분석)** | ⚠️ Java 필요 | ✅ | ✅ |
| **MeCab-ko** | ⚠️ 복잡 | ✅ | ✅ |

### 중요 주의사항
1. **모델 다운로드**: GLiNER 기반 도구는 첫 실행 시 1.2GB 모델 다운로드
2. **인터넷 연결**: 초기 설정 시 모델 다운로드를 위해 안정적인 인터넷 연결 필요
3. **Java 의존성**: KoNLPy 사용 시 Java 8+ 설치 필수 (Windows에서 특히 주의)
4. **한국어 특화**: 모든 도구는 한국어에 최적화되어 있음
5. **개인정보 처리**: 실제 개인정보 처리 시 관련 법규 준수 필요
6. **성능**: 첫 실행 시 모델 로딩으로 인한 지연 발생 가능

</details>

<details>
<summary><strong>🪟 Windows 환경 특별 주의사항</strong></summary>

#### 자주 발생하는 Windows 문제들

**1. 긴 경로명 문제**
```bash
# 오류: "The filename or extension is too long"
# 해결: 짧은 경로에 가상환경 생성
cd C:\
python -m venv venv_mask
C:\venv_mask\Scripts\activate

# 또는 긴 경로명 지원 활성화 (Windows 10+)
# 레지스트리 편집기 → HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
# LongPathsEnabled → 1로 변경
```

**2. 권한 문제**
```bash
# 오류: "Access is denied" 또는 "Permission denied"
# 해결: 관리자 권한으로 실행하거나 사용자 설치
pip install --user gliner spacy

# 또는 PowerShell을 관리자 권한으로 실행
# 시작 → PowerShell → 마우스 우클릭 → "관리자 권한으로 실행"
```

**3. Visual C++ 빌드 도구 누락**
```bash
# 오류: "Microsoft Visual C++ 14.0 is required"
# 해결: Visual Studio Build Tools 설치

# 방법 1: Visual Studio Installer에서 "C++ 빌드 도구" 설치
# 방법 2: 미리 컴파일된 패키지 사용
pip install --only-binary=all torch transformers

# 방법 3: conda 사용 (권장)
conda install pytorch transformers -c pytorch
```

**4. 인코딩 문제**
```bash
# 오류: "UnicodeDecodeError" 또는 한글 깨짐
# 해결: 환경변수 설정
set PYTHONIOENCODING=utf-8
set LANG=ko_KR.UTF-8

# 또는 Python 코드에서
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

**5. 방화벽/보안 소프트웨어 차단**
```bash
# 오류: 모델 다운로드 실패, 연결 타임아웃
# 해결: 
# 1. Windows Defender 방화벽에서 Python.exe 허용
# 2. 회사 보안 소프트웨어에서 Python 프로세스 허용
# 3. 프록시 설정
pip install --proxy http://proxy.company.com:8080 gliner

# 4. 수동 다운로드 후 오프라인 설치
# https://huggingface.co/taeminlee/gliner_ko 에서 수동 다운로드
```

**6. 메모리 부족 (32비트 Python)**
```bash
# 오류: "MemoryError" 또는 "Out of memory"
# 해결: 64비트 Python 사용 확인
python -c "import platform; print(platform.architecture())"
# ('64bit', 'WindowsPE') 출력되어야 함

# 32비트인 경우 64비트 Python 재설치 필요
```

#### Windows 환경 최적화 팁

**PowerShell 실행 정책 설정**
```powershell
# 스크립트 실행 허용
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 가상환경 활성화 스크립트 실행 허용
.\venv\Scripts\Activate.ps1
```

**환경변수 영구 설정**
```cmd
# 시스템 환경변수 설정 (관리자 권한 필요)
setx PYTHONIOENCODING "utf-8" /M
setx HF_HOME "C:\huggingface_cache" /M

# 사용자 환경변수 설정
setx PYTHONIOENCODING "utf-8"
setx HF_HOME "%USERPROFILE%\huggingface_cache"
```

### 기업 환경에서의 고려사항
- **방화벽**: 모델 다운로드를 위한 외부 접속 허용 필요
- **프록시**: 프록시 환경에서는 pip 및 모델 다운로드 설정 필요
- **보안**: 개인정보 처리 시 데이터 보안 정책 준수
- **라이선스**: 각 라이브러리의 라이선스 확인 필요
- **Windows 정책**: 그룹 정책으로 인한 설치 제한 확인

</details>

## 🤝 기여하기

버그 리포트, 기능 제안, 코드 기여를 환영합니다!

## 📄 라이선스

MIT License

---

**💡 빠른 시작**: 정확도가 중요하다면 `ModelBaseMasking.py`, 속도가 중요하다면 `spacyRulePatialMasking.py`를 추천합니다!
=======
# termRecognitionSample
text 데이터를 확인하여 term별 정보를 인식하고 민감정보를 masking 하기 위한 샘플코드
>>>>>>> 5b01f2ec88f0927f7f0081542cabe75f10d9db30
