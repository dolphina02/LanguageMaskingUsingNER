from gliner import GLiNER
import re

# 한국어 형태소 분석기 (선택사항)
try:
    from konlpy.tag import Okt
    okt = Okt()
    MORPHOLOGY_AVAILABLE = True
    print("✅ 한국어 형태소 분석기 로드 완료")
except ImportError:
    MORPHOLOGY_AVAILABLE = False
    print("⚠️ 형태소 분석기 없음 - 기본 정규식 사용")

def is_korean_name_with_morphology(text):
    """형태소 분석을 통한 한국어 이름 판별"""
    if not MORPHOLOGY_AVAILABLE:
        return True  # 형태소 분석기가 없으면 기본적으로 True
    
    try:
        # 형태소 분석으로 고유명사(NNP) 확인
        pos_tags = okt.pos(text)
        for word, pos in pos_tags:
            if pos == 'NNP':  # 고유명사
                return True
        return False
    except:
        return True  # 오류 시 기본적으로 True

def mask_name(name):
    """이름 부분 마스킹: 홍길동 → 홍*동"""
    if len(name) <= 1:
        return name
    elif len(name) == 2:
        return name[0] + '*'
    else:
        return name[0] + '*' * (len(name) - 2) + name[-1]

def mask_location(location):
    """지명 부분 마스킹: 서울 강남구 → 서* 강*구"""
    # 시/도/구/군/동 등의 행정구역 단위는 유지하고 지명만 마스킹
    location = re.sub(r'([가-힣]+)(?=시|도|구|군|읍|면|동|리)', lambda m: mask_name(m.group(1)), location)
    return location

def mask_organization(org):
    """기관명 부분 마스킹: 삼성병원 → 삼*원"""
    # 병원, 학교, 회사 등의 접미사는 유지
    if any(suffix in org for suffix in ['병원', '의원', '클리닉', '센터', '대학교', '학교', '회사', '기업']):
        # 접미사 앞의 기관명만 마스킹
        for suffix in ['병원', '의원', '클리닉', '센터', '대학교', '학교', '회사', '기업', '그룹', '재단']:
            if suffix in org:
                prefix = org.replace(suffix, '')
                if len(prefix) > 1:
                    masked_prefix = prefix[0] + '*' * (len(prefix) - 1)
                    return masked_prefix + suffix
                break
    
    # 일반적인 마스킹
    return mask_name(org)

def mask_date(date):
    """날짜 부분 마스킹: 2025년 6월 → 20**년 *월"""
    # 연도는 앞 2자리만 보이게, 월/일은 완전 마스킹
    date = re.sub(r'\d{4}(?=년)', lambda m: m.group()[:2] + '**', date)
    date = re.sub(r'\d+(?=월|일)', '*', date)
    return date

def mask_phone(phone):
    """전화번호 부분 마스킹: 010-1234-5678 → 010-1234-****"""
    if '-' in phone:
        parts = phone.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1]}-****"
        elif len(parts) == 2:
            return f"{parts[0]}-****"
    
    if phone.isdigit():
        if len(phone) == 11:  # 01012345678
            return phone[:7] + '****'
        elif len(phone) == 10:  # 0212345678
            return phone[:6] + '****'
    
    return phone

def mask_resident_number(rrn):
    """주민번호 부분 마스킹: 123456-1234567 → 123456-1******"""
    if '-' in rrn:
        front, back = rrn.split('-')
        return front + '-' + back[0] + '*' * (len(back) - 1)
    elif len(rrn) == 13:
        return rrn[:7] + '*' * 6
    return rrn

def mask_email(email):
    """이메일 부분 마스킹: user@domain.com → u***@domain.com"""
    if '@' in email:
        username, domain = email.split('@', 1)
        if len(username) > 1:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username
        return masked_username + '@' + domain
    return email

def partial_mask_entity(text, entity_type):
    """엔티티 타입에 따른 부분 마스킹"""
    if entity_type in ["PERSON", "DOCTOR"]:
        # 조사 분리
        clean_text = re.sub(r'[은는이가을를에게께서님씨군양]$', '', text)
        suffix = text[len(clean_text):]
        return mask_name(clean_text) + suffix
    
    elif entity_type in ["LOCATION", "ADDRESS"]:
        return mask_location(text)
    
    elif entity_type in ["ORGANIZATION", "HOSPITAL"]:
        return mask_organization(text)
    
    elif entity_type in ["DATE", "TIME"]:
        return mask_date(text)
    
    elif entity_type in ["PHONE"]:
        return mask_phone(text)
    
    elif entity_type in ["EMAIL"]:
        return mask_email(text)
    
    elif entity_type in ["ID", "PASSPORT", "LICENSE", "VEHICLE"]:
        # 식별번호류는 앞 몇자리만 보이게
        if len(text) > 4:
            return text[:2] + '*' * (len(text) - 4) + text[-2:]
        else:
            return '*' * len(text)
    
    elif entity_type in ["MONEY", "FINANCIAL", "BANK_ACCOUNT", "CREDIT_CARD"]:
        # 금융정보는 뒤 4자리만 보이게
        if len(text) > 4:
            return '*' * (len(text) - 4) + text[-4:]
        else:
            return '*' * len(text)
    
    elif entity_type in ["MEDICAL", "DISEASE", "MEDICINE"]:
        # 의료정보는 첫글자와 마지막글자만 보이게
        if len(text) <= 2:
            return text[0] + '*' * (len(text) - 1)
        else:
            return text[0] + '*' * (len(text) - 2) + text[-1]
    
    elif entity_type in ["AGE"]:
        # 나이는 십의 자리만 보이게 (20대, 30대 등)
        age_match = re.search(r'\d+', text)
        if age_match:
            age = int(age_match.group())
            decade = (age // 10) * 10
            return text.replace(str(age), f"{decade}대")
        return text
    
    elif entity_type in ["PERCENT"]:
        # 퍼센트는 대략적인 범위로
        percent_match = re.search(r'\d+', text)
        if percent_match:
            percent = int(percent_match.group())
            if percent < 10:
                return "10% 미만"
            elif percent < 50:
                return "50% 미만"
            else:
                return "50% 이상"
        return text
    
    elif entity_type in ["PASSWORD", "BIOMETRIC"]:
        # 완전 마스킹
        return '*' * len(text)
    
    elif entity_type in ["IP_ADDRESS", "URL", "USERNAME"]:
        # 부분 마스킹
        if len(text) > 6:
            return text[:3] + '*' * (len(text) - 6) + text[-3:]
        else:
            return text[0] + '*' * (len(text) - 1)
    
    else:
        # 기타 엔티티는 일반적인 부분 마스킹
        return mask_name(text)

# 전역 모델 인스턴스 (메모리 효율성 개선)
_gliner_model = None

def get_gliner_model():
    """GLiNER 모델 싱글톤 패턴"""
    global _gliner_model
    if _gliner_model is None:
        print("GLiNER 모델 로딩 중... (1회만 실행)")
        _gliner_model = GLiNER.from_pretrained("taeminlee/gliner_ko")
        print("GLiNER 모델 로딩 완료!")
    return _gliner_model

def model_based_partial_masking(text, labels=None, threshold=0.90):
    """GLiNER 모델 기반 부분 마스킹 (개선된 버전)"""
    
    # 모델 로드 (싱글톤 패턴)
    model = get_gliner_model()
    
    # 기본 라벨 설정 - GLiNER가 감지할 수 있는 다양한 엔티티 타입들
    if labels is None:
        labels = [
            "PERSON",           # 인명
            "LOCATION",         # 지명
            "ORGANIZATION",     # 기관/조직
            "DATE",            # 날짜
            "TIME",            # 시간
            "MONEY",           # 금액
            "PERCENT",         # 퍼센트
            "PHONE",           # 전화번호
            "EMAIL",           # 이메일
            "ADDRESS",         # 주소
            "ID",              # 식별번호
            "MEDICAL",         # 의료정보
            "DISEASE",         # 질병명
            "MEDICINE",        # 약물명
            "HOSPITAL",        # 병원명
            "DOCTOR",          # 의사명
            "AGE",             # 나이
            "OCCUPATION",      # 직업
            "NATIONALITY",     # 국적
            "RELIGION",        # 종교
            "POLITICAL",       # 정치성향
            "EDUCATION",       # 학력
            "FAMILY",          # 가족관계
            "FINANCIAL",       # 금융정보
            "CREDIT_CARD",     # 신용카드
            "BANK_ACCOUNT",    # 계좌번호
            "LICENSE",         # 면허번호
            "PASSPORT",        # 여권번호
            "VEHICLE",         # 차량번호
            "IP_ADDRESS",      # IP주소
            "URL",             # 웹주소
            "USERNAME",        # 사용자명
            "PASSWORD",        # 비밀번호
            "BIOMETRIC"        # 생체정보
        ]
    
    # 추가 정규식 패턴으로 전화번호, 주민번호, 이메일 먼저 처리
    masked_text = text
    masked_items = []
    
    # 1. 주민번호 마스킹
    rrn_patterns = [r'\d{6}-\d{7}', r'\d{13}']
    for pattern in rrn_patterns:
        for match in re.finditer(pattern, masked_text):
            original_rrn = match.group()
            masked_rrn = mask_resident_number(original_rrn)
            masked_text = masked_text.replace(original_rrn, masked_rrn)
            masked_items.append(f"주민번호: {original_rrn} → {masked_rrn}")
    
    # 2. 전화번호 마스킹
    phone_patterns = [
        r'\d{3}-\d{4}-\d{4}',  # 010-1234-5678
        r'\d{3}-\d{3}-\d{4}',   # 010-123-4567
        r'\d{2,3}-\d{3,4}-\d{4}',  # 02-1234-5678
    ]
    
    for pattern in phone_patterns:
        for match in re.finditer(pattern, masked_text):
            original_phone = match.group()
            masked_phone = mask_phone(original_phone)
            masked_text = masked_text.replace(original_phone, masked_phone)
            masked_items.append(f"전화번호: {original_phone} → {masked_phone}")
    
    # 3. 이메일 마스킹
    email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
    for match in re.finditer(email_pattern, masked_text):
        original_email = match.group()
        masked_email = mask_email(original_email)
        masked_text = masked_text.replace(original_email, masked_email)
        masked_items.append(f"이메일: {original_email} → {masked_email}")
    
    # 4. GLiNER 모델로 엔티티 감지
    entities = model.predict_entities(masked_text, labels)
    
    # 마스킹 대상만 필터링
    sensitive_entities = [e for e in entities if e["score"] >= threshold]
    
    # 위치별 정렬 (뒤에서부터 바꾸기 위함 → index 꼬임 방지)
    sensitive_entities = sorted(sensitive_entities, key=lambda e: e['start'], reverse=True)
    
    # 5. 엔티티별 부분 마스킹 적용
    for e in sensitive_entities:
        original_text = e['text']
        masked_entity = partial_mask_entity(original_text, e['label'])
        masked_text = masked_text[:e['start']] + masked_entity + masked_text[e['end']:]
        masked_items.append(f"{e['label']}: {original_text} → {masked_entity} (신뢰도: {e['score']:.2f})")
    
    return masked_text, masked_items

# 테스트 실행
if __name__ == "__main__":
    # 예제 문장들 - 다양한 개인정보 유형 포함
    test_cases = [
        "홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 2025년 6월에 1달간 병원에 있었어요.",
        "김철수(010-1234-5678)는 부산대학교병원에서 고혈압 진료를 받았습니다.",
        "이영희님의 주민번호는 123456-1234567이고, 이메일은 test@example.com입니다.",
        "박민수 환자가 현대자동차에 다니며, 서울시 종로구 세종대로 123번지에 살고 있습니다.",
        "정수진(35세)은 당뇨병으로 인슐린을 투약 중이며, 연봉은 5000만원입니다.",
        "최영호 의사는 오후 3시에 진료하며, 면허번호는 ABC123456입니다.",
        "강민수는 12가-3456 차량을 소유하고 있으며, 계좌번호는 110-123-456789입니다.",
        "윤서연은 https://example.com에서 일하며, 사용자명은 user123입니다."
    ]
    
    print("🔒 GLiNER 모델 기반 부분 마스킹 테스트")
    print("=" * 80)
    
    # 파일 처리 함수들 추가
    def process_single_file(input_file_path, output_file_path, encoding='utf-8'):
        """단일 파일 처리"""
        try:
            print(f"📂 파일 읽기: {input_file_path}")
            
            # 파일 읽기
            with open(input_file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            print(f"📊 총 {len(lines)}줄 처리 시작...")
            
            # 각 줄 마스킹 처리
            masked_lines = []
            total_masked_items = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line:  # 빈 줄이 아닌 경우만 처리
                    try:
                        masked_text, masked_items = model_based_partial_masking(line)
                        masked_lines.append(masked_text + '\n')
                        total_masked_items.extend(masked_items)
                        
                        if i % 100 == 0:  # 100줄마다 진행상황 출력
                            print(f"진행률: {i}/{len(lines)} ({i/len(lines)*100:.1f}%)")
                    except Exception as e:
                        print(f"⚠️ {i}번째 줄 처리 오류: {e}")
                        masked_lines.append(line + '\n')  # 원본 유지
                else:
                    masked_lines.append('\n')  # 빈 줄 유지
            
            # 결과 파일 저장
            print(f"💾 결과 저장: {output_file_path}")
            with open(output_file_path, 'w', encoding=encoding) as f:
                f.writelines(masked_lines)
            
            print(f"✅ 처리 완료!")
            print(f"📋 총 마스킹된 항목: {len(total_masked_items)}개")
            
            # 마스킹 통계
            if total_masked_items:
                from collections import Counter
                item_types = [item.split(':')[0] for item in total_masked_items]
                stats = Counter(item_types)
                print("📊 마스킹 통계:")
                for item_type, count in stats.most_common():
                    print(f"  - {item_type}: {count}개")
            
            return True, total_masked_items
            
        except Exception as e:
            print(f"❌ 파일 처리 실패: {e}")
            return False, []
    
    def process_multiple_files(input_dir, output_dir, file_pattern="*.txt", encoding='utf-8'):
        """여러 파일 배치 처리"""
        import glob
        import os
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 입력 파일 목록 가져오기
        input_pattern = os.path.join(input_dir, file_pattern)
        input_files = glob.glob(input_pattern)
        
        if not input_files:
            print(f"❌ 파일을 찾을 수 없습니다: {input_pattern}")
            return
        
        print(f"📁 {len(input_files)}개 파일 처리 시작...")
        
        success_count = 0
        total_masked_items = []
        
        for i, input_file in enumerate(input_files, 1):
            filename = os.path.basename(input_file)
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}_masked{ext}")
            
            print(f"\n[{i}/{len(input_files)}] 처리 중: {filename}")
            
            success, masked_items = process_single_file(input_file, output_file, encoding)
            if success:
                success_count += 1
                total_masked_items.extend(masked_items)
        
        print(f"\n🎉 배치 처리 완료!")
        print(f"✅ 성공: {success_count}/{len(input_files)} 파일")
        print(f"📋 총 마스킹된 항목: {len(total_masked_items)}개")
        
        return success_count, total_masked_items
    
    def main_local_processing(srcDir=None, tgtDir=None, file_pattern="*.txt", encoding='utf-8'):
        """메인 로컬 파일 처리 함수"""
        
        print("🔒 GLiNER 모델 기반 로컬 파일 마스킹 도구")
        print("=" * 60)
        
        # 기본 디렉토리 설정
        if srcDir is None:
            srcDir = input("📂 소스 디렉토리 경로를 입력하세요 (예: ./input/): ").strip()
            if not srcDir:
                srcDir = "./input/"
        
        if tgtDir is None:
            tgtDir = input("📁 타겟 디렉토리 경로를 입력하세요 (예: ./output/): ").strip()
            if not tgtDir:
                tgtDir = "./output/"
        
        print(f"📂 소스 디렉토리: {srcDir}")
        print(f"📁 타겟 디렉토리: {tgtDir}")
        print(f"🔍 파일 패턴: {file_pattern}")
        
        # 디렉토리 존재 확인
        import os
        if not os.path.exists(srcDir):
            print(f"❌ 소스 디렉토리가 존재하지 않습니다: {srcDir}")
            
            # 데모용 디렉토리 및 파일 생성
            print("🧪 데모용 파일 생성...")
            os.makedirs(srcDir, exist_ok=True)
            
            # 테스트 파일들 생성
            test_files = {
                "sample1.txt": """홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 2025년 6월에 1달간 병원에 있었어요.
김철수(010-1234-5678)는 부산대학교병원에서 고혈압 진료를 받았습니다.""",
                
                "sample2.txt": """이영희님의 주민번호는 123456-1234567이고, 이메일은 test@example.com입니다.
박민수 환자가 현대자동차에 다니며, 서울시 종로구 세종대로 123번지에 살고 있습니다.""",
                
                "sample3.txt": """정수진(35세)은 당뇨병으로 인슐린을 투약 중이며, 연봉은 5000만원입니다.
최영호 의사는 오후 3시에 진료하며, 면허번호는 ABC123456입니다.
강민수는 12가-3456 차량을 소유하고 있으며, 계좌번호는 110-123-456789입니다."""
            }
            
            for filename, content in test_files.items():
                filepath = os.path.join(srcDir, filename)
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(content)
                print(f"✅ 생성됨: {filepath}")
        
        # 배치 처리 실행
        success_count, total_masked_items = process_multiple_files(srcDir, tgtDir, file_pattern, encoding)
        
        return {
            'srcDir': srcDir,
            'tgtDir': tgtDir,
            'success_count': success_count,
            'total_masked_items': len(total_masked_items),
            'file_pattern': file_pattern
        }
    
    # 사용 예시 및 실행
    if __name__ == "__main__":
        import sys
        
        # 명령행 인자 처리
        if len(sys.argv) >= 3:
            srcDir = sys.argv[1]
            tgtDir = sys.argv[2]
            file_pattern = sys.argv[3] if len(sys.argv) > 3 else "*.txt"
            
            print("📝 명령행 인자로 실행:")
            print(f"python ModelBaseMasking.py {srcDir} {tgtDir} {file_pattern}")
            
            result = main_local_processing(srcDir, tgtDir, file_pattern)
            
        else:
            print("📝 사용법:")
            print("1. 대화형 실행: python ModelBaseMasking.py")
            print("2. 명령행 실행: python ModelBaseMasking.py <srcDir> <tgtDir> [file_pattern]")
            print("   예시: python ModelBaseMasking.py ./input/ ./output/ *.txt")
            print()
            
            # 대화형 실행
            result = main_local_processing()
        
        print(f"\n🎉 처리 완료!")
        print(f"📊 결과 요약:")
        print(f"  - 소스: {result['srcDir']}")
        print(f"  - 타겟: {result['tgtDir']}")
        print(f"  - 성공 파일: {result['success_count']}개")
        print(f"  - 마스킹 항목: {result['total_masked_items']}개")