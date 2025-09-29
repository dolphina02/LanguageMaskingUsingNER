import spacy
import re

# 한국어 모델 로드
nlp = spacy.load("ko_core_news_sm")

def mask_name(name):
    """이름 부분 마스킹: 홍길동 → 홍*동"""
    if len(name) <= 1:
        return name
    elif len(name) == 2:
        return name[0] + '*'
    else:
        return name[0] + '*' * (len(name) - 2) + name[-1]

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

def is_korean_name(text):
    """한국 이름인지 판단하는 함수"""
    # 일반적인 한국 성씨 목록 (상위 100개 성씨)
    korean_surnames = [
        '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안',
        '송', '류', '전', '홍', '고', '문', '양', '손', '배', '조', '백', '허', '유', '남', '심', '노', '정',
        '하', '곽', '성', '차', '주', '우', '구', '신', '임', '나', '전', '민', '유', '진', '지', '엄', '채',
        '원', '천', '방', '공', '강', '현', '함', '변', '염', '양', '변', '여', '추', '노', '도', '소', '신',
        '석', '선', '설', '마', '길', '주', '연', '방', '위', '표', '명', '기', '반', '왕', '금', '옥', '육',
        '인', '맹', '제', '모', '장', '남', '탁', '국', '여', '진', '어', '은', '편', '구', '용'
    ]
    
    # 2-4글자이고 첫 글자가 한국 성씨인 경우
    if 2 <= len(text) <= 4 and text[0] in korean_surnames:
        return True
    return False

def final_masking(text):
    """최종 개선된 부분 마스킹"""
    
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
    
    # 4. 한국 이름 마스킹 (더 정확한 패턴)
    name_patterns = [
        r'[가-힣]{2,4}(?=은|는|이|가|을|를|에게|께서)',  # 조사가 붙은 이름
        r'[가-힣]{2,4}(?:님|씨)',  # 호칭이 붙은 이름
    ]
    
    for pattern in name_patterns:
        for match in re.finditer(pattern, masked_text):
            original_name = match.group()
            
            # 호칭 분리
            name_part = re.sub(r'(님|씨)$', '', original_name)
            suffix = original_name[len(name_part):]
            
            # 실제 한국 이름인지 확인
            if is_korean_name(name_part):
                masked_name = mask_name(name_part) + suffix
                masked_text = masked_text.replace(original_name, masked_name)
                masked_items.append(f"이름: {original_name} → {masked_name}")
    
    # 5. 질병/의료정보 마스킹
    medical_terms = [
        '당뇨병', '고혈압', '저혈압', '심장병', '뇌졸중', '치매', '우울증', '불안장애',
        '간염', '신부전', '폐렴', '결핵', '천식', '아토피', '알레르기', '골절',
        '암', '백혈병', '림프종', '위암', '폐암', '간암', '대장암', '유방암',
        '갑상선암', '전립선암', '자궁암', '난소암', '췌장암', '신장암', '방광암'
    ]
    
    for term in medical_terms:
        if term in masked_text:
            if len(term) == 1:
                masked_term = '*'
            elif len(term) == 2:
                masked_term = term[0] + '*'
            else:
                masked_term = term[0] + '*' * (len(term) - 2) + term[-1]
            
            masked_text = masked_text.replace(term, masked_term)
            masked_items.append(f"의료정보: {term} → {masked_term}")
    
    # 6. 주소 번지수/호수 마스킹
    address_patterns = [r'\d+번지', r'\d+호', r'\d+층']
    for pattern in address_patterns:
        for match in re.finditer(pattern, masked_text):
            original_addr = match.group()
            masked_addr = re.sub(r'\d+', lambda m: '*' * len(m.group()), original_addr)
            masked_text = masked_text.replace(original_addr, masked_addr)
            masked_items.append(f"주소: {original_addr} → {masked_addr}")
    
    return masked_text, masked_items

# 테스트
if __name__ == "__main__":
    test_cases = [
        "홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 당뇨병 치료를 받았어요.",
        "김철수(010-1234-5678)는 부산대학교병원에서 고혈압 진료를 받았습니다.",
        "이영희님의 주민번호는 123456-1234567이고, 이메일은 test@example.com입니다.",
        "박민수 환자가 현대자동차에 다니며, 서울시 종로구 세종대로 123번지에 살고 있습니다.",
        "최지훈 교수(02-1234-5678)가 연세대학교에서 암 연구를 하고 있습니다.",
        "정수진씨는 010-9876-5432로 연락 가능하며, 위암 수술을 받았습니다.",
        "강민호님(abc123@gmail.com)이 부산시 해운대구 센텀로 99번지 15층에 거주합니다.",
        "조영수는 1234567890123 주민번호를 가지고 있고, 폐암 진단을 받았습니다."
    ]
    
    print("🔒 최종 부분 마스킹 테스트")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n테스트 {i}:")
        print(f"원본: {text}")
        
        masked_text, masked_items = final_masking(text)
        print(f"마스킹: {masked_text}")
        
        if masked_items:
            print("마스킹된 항목:")
            for item in masked_items:
                print(f"  - {item}")
        else:
            print("마스킹된 항목: 없음")