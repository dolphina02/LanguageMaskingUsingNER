import re

def simple_masking(text):
    """간단한 정규식 기반 마스킹"""
    
    # 한국 이름 패턴 (2-4글자)
    name_pattern = r'\b[가-힣]{2,4}(?=은|는|이|가|을|를|에게|께서|님|씨)\b'
    
    # 지역명 패턴
    location_pattern = r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[시도구군]?(?:\s+[가-힣]+[구동읍면리])?'
    
    # 병원/기관명 패턴
    org_pattern = r'[가-힣]+(?:병원|의원|클리닉|센터|대학교|학교|회사|기업|그룹)'
    
    # 날짜 패턴
    date_pattern = r'\d{4}년\s*\d{1,2}월|\d{1,2}월(?:\s*\d{1,2}일)?'
    
    # 마스킹 적용
    masked_text = text
    masked_text = re.sub(name_pattern, '[PERSON]', masked_text)
    masked_text = re.sub(location_pattern, '[LOCATION]', masked_text)
    masked_text = re.sub(org_pattern, '[ORGANIZATION]', masked_text)
    masked_text = re.sub(date_pattern, '[DATE]', masked_text)
    
    return masked_text

# 테스트
text = "홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 2025년 6월에 1달간 병원에 있었어요."

print("🔹 원본 문장:")
print(text)
print("\n🔒 마스킹된 문장:")
print(simple_masking(text))

print("\n" + "="*50)
print("추가 테스트:")

test_cases = [
    "김철수는 부산대학교병원에서 치료받았습니다.",
    "이영희가 2024년 3월 15일에 서울시 종로구에 방문했어요.",
    "박민수님이 현대자동차에 다니고 있습니다."
]

for i, test in enumerate(test_cases, 1):
    print(f"\n테스트 {i}:")
    print(f"원본: {test}")
    print(f"마스킹: {simple_masking(test)}")