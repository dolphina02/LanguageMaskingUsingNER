# 방법 1: 전역 변수 방식 (가장 간단)
from gliner import GLiNER

# 전역 변수로 모델 저장
_gliner_model = None

def get_gliner_model():
    """전역 변수를 이용한 싱글톤"""
    global _gliner_model
    
    if _gliner_model is None:  # 처음 호출 시에만 로딩
        print("🔄 GLiNER 모델 로딩 중... (1회만 실행)")
        _gliner_model = GLiNER.from_pretrained("taeminlee/gliner_ko")
        print("✅ GLiNER 모델 로딩 완료!")
    else:
        print("♻️ 기존 모델 재사용")
    
    return _gliner_model

# 테스트
print("=== 전역 변수 방식 테스트 ===")
model1 = get_gliner_model()  # 첫 번째 호출 - 로딩
model2 = get_gliner_model()  # 두 번째 호출 - 재사용
model3 = get_gliner_model()  # 세 번째 호출 - 재사용

print(f"model1 id: {id(model1)}")
print(f"model2 id: {id(model2)}")
print(f"model3 id: {id(model3)}")
print(f"같은 객체인가? {model1 is model2 is model3}")

print("\n" + "="*50 + "\n")

# 방법 2: 클래스 기반 싱글톤 (더 정교함)
class GLiNERSingleton:
    _instance = None  # 클래스 변수로 인스턴스 저장
    _model = None     # 클래스 변수로 모델 저장
    
    def __new__(cls):
        """새 인스턴스 생성을 제어"""
        if cls._instance is None:
            print("🆕 GLiNERSingleton 인스턴스 생성")
            cls._instance = super(GLiNERSingleton, cls).__new__(cls)
        else:
            print("♻️ 기존 GLiNERSingleton 인스턴스 재사용")
        return cls._instance
    
    def get_model(self):
        """모델 반환 (필요시 로딩)"""
        if GLiNERSingleton._model is None:
            print("🔄 GLiNER 모델 로딩 중... (클래스 방식)")
            GLiNERSingleton._model = GLiNER.from_pretrained("taeminlee/gliner_ko")
            print("✅ GLiNER 모델 로딩 완료!")
        else:
            print("♻️ 기존 모델 재사용")
        return GLiNERSingleton._model

# 테스트
print("=== 클래스 기반 싱글톤 테스트 ===")
singleton1 = GLiNERSingleton()
singleton2 = GLiNERSingleton()
singleton3 = GLiNERSingleton()

print(f"singleton1 id: {id(singleton1)}")
print(f"singleton2 id: {id(singleton2)}")
print(f"singleton3 id: {id(singleton3)}")
print(f"같은 인스턴스인가? {singleton1 is singleton2 is singleton3}")

model_a = singleton1.get_model()  # 첫 번째 모델 로딩
model_b = singleton2.get_model()  # 재사용
model_c = singleton3.get_model()  # 재사용

print(f"model_a id: {id(model_a)}")
print(f"model_b id: {id(model_b)}")
print(f"model_c id: {id(model_c)}")
print(f"같은 모델인가? {model_a is model_b is model_c}")

print("\n" + "="*50 + "\n")

# 방법 3: 데코레이터 방식 (함수형)
def singleton_decorator(func):
    """싱글톤 데코레이터"""
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            print(f"🔄 {func.__name__} 첫 실행 - 결과 캐싱")
            cache[key] = func(*args, **kwargs)
        else:
            print(f"♻️ {func.__name__} 캐시된 결과 반환")
        return cache[key]
    
    return wrapper

@singleton_decorator
def load_gliner_model():
    """데코레이터를 이용한 싱글톤 모델 로딩"""
    print("🔄 GLiNER 모델 로딩 중... (데코레이터 방식)")
    model = GLiNER.from_pretrained("taeminlee/gliner_ko")
    print("✅ GLiNER 모델 로딩 완료!")
    return model

# 테스트
print("=== 데코레이터 방식 테스트 ===")
model_x = load_gliner_model()  # 첫 번째 호출 - 로딩
model_y = load_gliner_model()  # 두 번째 호출 - 캐시 반환
model_z = load_gliner_model()  # 세 번째 호출 - 캐시 반환

print(f"model_x id: {id(model_x)}")
print(f"model_y id: {id(model_y)}")
print(f"model_z id: {id(model_z)}")
print(f"같은 모델인가? {model_x is model_y is model_z}")

print("\n" + "="*50 + "\n")

# 방법 4: 모듈 레벨 싱글톤 (Python의 특성 활용)
class ModelManager:
    """모듈 레벨에서 관리되는 싱글톤"""
    def __init__(self):
        self._model = None
        print("🆕 ModelManager 생성")
    
    def get_model(self):
        if self._model is None:
            print("🔄 GLiNER 모델 로딩 중... (모듈 방식)")
            self._model = GLiNER.from_pretrained("taeminlee/gliner_ko")
            print("✅ GLiNER 모델 로딩 완료!")
        else:
            print("♻️ 기존 모델 재사용")
        return self._model

# 모듈 레벨에서 인스턴스 생성 (import 시 1회만 실행)
model_manager = ModelManager()

def get_model_from_manager():
    """모듈 레벨 싱글톤 접근 함수"""
    return model_manager.get_model()

# 테스트
print("=== 모듈 레벨 싱글톤 테스트 ===")
model_1 = get_model_from_manager()  # 첫 번째 호출
model_2 = get_model_from_manager()  # 두 번째 호출
model_3 = get_model_from_manager()  # 세 번째 호출

print(f"model_1 id: {id(model_1)}")
print(f"model_2 id: {id(model_2)}")
print(f"model_3 id: {id(model_3)}")
print(f"같은 모델인가? {model_1 is model_2 is model_3}")

print("\n" + "="*50 + "\n")

# 실제 사용 예시
def process_text_with_singleton(text):
    """싱글톤 패턴을 사용한 텍스트 처리"""
    model = get_gliner_model()  # 항상 같은 모델 인스턴스 반환
    
    # 실제 처리 로직
    labels = ["PERSON", "LOCATION", "ORGANIZATION"]
    entities = model.predict_entities(text, labels)
    
    return entities

# 여러 번 호출해도 모델은 1회만 로딩
texts = [
    "홍길동은 서울에 살고 있습니다.",
    "김철수가 부산대학교에 다닙니다.",
    "이영희는 삼성전자에서 일합니다."
]

print("=== 실제 사용 예시 ===")
for i, text in enumerate(texts, 1):
    print(f"\n텍스트 {i}: {text}")
    entities = process_text_with_singleton(text)
    print(f"감지된 엔티티: {len(entities)}개")