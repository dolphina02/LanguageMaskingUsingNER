import spacy
import re

# 한국어 모델 로드
nlp = spacy.load("ko_core_news_sm")

def spacy_masking(text, threshold=0.5):
    """spaCy를 사용한 개인정보 마스킹"""
    
    # spaCy로 문서 처리
    doc = nlp(text)
    
    # 엔티티 정보 수집 (뒤에서부터 처리하기 위해 역순 정렬)
    entities = []
    for ent in doc.ents:
        entities.append({
            'start': ent.start_char,
            'end': ent.end_char,
            'label': ent.label_,
            'text': ent.text,
            'confidence': 1.0  # spaCy는 기본적으로 confidence score를 제공하지 않음
        })
    
    # 추가 정규식 패턴으로 보완
    additional_patterns = {
        'PERSON': [
            r'\b[가-힣]{2,4}(?=은|는|이|가|을|를|에게|께서|님|씨)\b',  # 한국 이름
            r'\b[가-힣]{2,4}(?:님|씨|군|양)\b'  # 호칭이 붙은 이름
        ],
        'ORG': [
            r'[가-힣]+(?:병원|의원|클리닉|센터|대학교|학교|회사|기업|그룹|재단|협회)\b',
            r'(?:삼성|LG|현대|SK|롯데|한화|GS|포스코|신한|KB|우리|하나)[가-힣]*\b'
        ],
        'DATE': [
            r'\d{4}년\s*\d{1,2}월(?:\s*\d{1,2}일)?',
            r'\d{1,2}월\s*\d{1,2}일',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ],
        'GPE': [  # 지명
            r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[시도]?(?:\s+[가-힣]+[구군])?(?:\s+[가-힣]+[동읍면리])?'
        ]
    }
    
    # 정규식으로 추가 엔티티 찾기
    for label, patterns in additional_patterns.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                # 기존 엔티티와 겹치지 않는 경우만 추가
                overlap = False
                for existing in entities:
                    if (match.start() < existing['end'] and match.end() > existing['start']):
                        overlap = True
                        break
                
                if not overlap:
                    entities.append({
                        'start': match.start(),
                        'end': match.end(),
                        'label': label,
                        'text': match.group(),
                        'confidence': 0.8
                    })
    
    # 위치별 역순 정렬 (뒤에서부터 바꾸기 위함)
    entities = sorted(entities, key=lambda x: x['start'], reverse=True)
    
    # 마스킹 적용
    masked_text = text
    for ent in entities:
        if ent['confidence'] >= threshold:
            # 라벨에 따른 마스킹
            if ent['label'] in ['PERSON', 'PER', 'PS']:
                replacement = '[PERSON]'
            elif ent['label'] in ['ORG', 'ORGANIZATION', 'OG']:
                replacement = '[ORGANIZATION]'
            elif ent['label'] in ['GPE', 'LOC', 'LOCATION', 'LC']:
                replacement = '[LOCATION]'
            elif ent['label'] in ['DATE', 'DT']:
                replacement = '[DATE]'
            else:
                replacement = f"[{ent['label']}]"
            
            masked_text = masked_text[:ent['start']] + replacement + masked_text[ent['end']:]
    
    return masked_text, entities

# 테스트
if __name__ == "__main__":
    # 예제 문장
    text = "홍길동은 서울 강남구에서 사는데, 삼성병원에 입원했고, 2025년 6월에 1달간 병원에 있었어요."
    
    print("🔹 원본 문장:")
    print(text)
    
    masked_text, entities = spacy_masking(text)
    
    print("\n🔒 마스킹된 문장:")
    print(masked_text)
    
    print("\n📋 감지된 엔티티:")
    for ent in sorted(entities, key=lambda x: x['start']):
        print(f"  - {ent['text']} → {ent['label']} (신뢰도: {ent['confidence']:.2f})")
    
    print("\n" + "="*60)
    print("추가 테스트:")
    
    test_cases = [
        "김철수는 부산대학교병원에서 치료받았습니다.",
        "이영희가 2024년 3월 15일에 서울시 종로구에 방문했어요.",
        "박민수님이 현대자동차에 다니고 있습니다.",
        "최지훈 교수가 연세대학교에서 강의를 합니다."
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}:")
        print(f"원본: {test}")
        masked, ents = spacy_masking(test)
        print(f"마스킹: {masked}")
        if ents:
            print("감지된 엔티티:", [f"{e['text']}({e['label']})" for e in sorted(ents, key=lambda x: x['start'])])