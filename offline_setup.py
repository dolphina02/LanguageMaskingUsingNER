#!/usr/bin/env python3
"""
폐쇄망 환경을 위한 오프라인 패키지 다운로드 스크립트
온라인 환경에서 실행하여 필요한 모든 패키지를 다운로드합니다.
"""

import os
import subprocess
import sys
import urllib.request
from pathlib import Path

def run_command(cmd, description=""):
    """명령어 실행 및 결과 출력"""
    print(f"🔄 {description}")
    print(f"실행: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ 성공: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {description}")
        print(f"오류: {e.stderr}")
        return False

def download_file(url, filepath, description=""):
    """파일 다운로드"""
    print(f"🔄 {description}")
    print(f"다운로드: {url}")
    
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ 다운로드 완료: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return False

def create_offline_packages():
    """오프라인 패키지 생성"""
    
    print("🔒 폐쇄망 환경용 오프라인 패키지 생성 도구")
    print("=" * 60)
    
    # 기본 디렉토리 생성
    base_dir = Path("offline_packages")
    base_dir.mkdir(exist_ok=True)
    
    packages_dir = base_dir / "packages"
    models_dir = base_dir / "models"
    scripts_dir = base_dir / "scripts"
    
    packages_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)
    
    print(f"📁 작업 디렉토리: {base_dir.absolute()}")
    
    # 1. 기본 패키지 다운로드
    print("\n📦 1단계: 기본 패키지 다운로드")
    basic_packages = [
        "pandas", "numpy", "regex", "tqdm", "requests"
    ]
    
    for package in basic_packages:
        run_command(
            f"pip download --dest {packages_dir} {package}",
            f"기본 패키지 다운로드: {package}"
        )
    
    # 2. GLiNER 관련 패키지 다운로드
    print("\n🤖 2단계: GLiNER 관련 패키지 다운로드")
    gliner_packages = [
        "gliner", "torch", "transformers", "huggingface_hub", 
        "safetensors", "tokenizers", "filelock"
    ]
    
    for package in gliner_packages:
        run_command(
            f"pip download --dest {packages_dir} {package}",
            f"GLiNER 패키지 다운로드: {package}"
        )
    
    # 3. spaCy 관련 패키지 다운로드
    print("\n🔍 3단계: spaCy 관련 패키지 다운로드")
    spacy_packages = [
        "spacy", "spacy-legacy", "spacy-loggers", "murmurhash", 
        "cymem", "preshed", "thinc", "wasabi", "srsly", "catalogue"
    ]
    
    for package in spacy_packages:
        run_command(
            f"pip download --dest {packages_dir} {package}",
            f"spaCy 패키지 다운로드: {package}"
        )
    
    # spaCy 한국어 모델 다운로드
    spacy_model_url = "https://github.com/explosion/spacy-models/releases/download/ko_core_news_sm-3.8.0/ko_core_news_sm-3.8.0-py3-none-any.whl"
    spacy_model_file = packages_dir / "ko_core_news_sm-3.8.0-py3-none-any.whl"
    
    download_file(spacy_model_url, spacy_model_file, "spaCy 한국어 모델 다운로드")
    
    # 4. 한국어 형태소 분석기 패키지 다운로드
    print("\n🔤 4단계: 한국어 형태소 분석기 다운로드")
    morphology_packages = [
        "konlpy", "eunjeon", "soynlp"
    ]
    
    for package in morphology_packages:
        run_command(
            f"pip download --dest {packages_dir} {package}",
            f"형태소 분석기 다운로드: {package}"
        )
    
    # 5. Databricks/Spark 패키지 다운로드
    print("\n⚡ 5단계: Databricks/Spark 패키지 다운로드")
    spark_packages = [
        "pyspark", "py4j", "pyarrow"
    ]
    
    for package in spark_packages:
        run_command(
            f"pip download --dest {packages_dir} {package}",
            f"Spark 패키지 다운로드: {package}"
        )
    
    # 6. GLiNER 모델 다운로드 안내
    print("\n🤖 6단계: GLiNER 모델 수동 다운로드 안내")
    print("다음 URL에서 모델 파일들을 수동으로 다운로드해야 합니다:")
    print("https://huggingface.co/taeminlee/gliner_ko")
    print("\n필요한 파일들:")
    model_files = [
        "config.json",
        "pytorch_model.bin (1.21GB)",
        "tokenizer_config.json", 
        "vocab.txt",
        "special_tokens_map.json"
    ]
    
    for file in model_files:
        print(f"  - {file}")
    
    print(f"\n다운로드한 파일들을 {models_dir} 폴더에 저장하세요.")
    
    # 7. 설치 스크립트 생성
    print("\n📝 7단계: 설치 스크립트 생성")
    
    # Windows 설치 스크립트
    windows_script = scripts_dir / "install_windows.bat"
    with open(windows_script, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo 폐쇄망 환경 오프라인 설치 스크립트 (Windows)
echo ================================================

echo 가상환경 생성...
python -m venv venv
call venv\\Scripts\\activate.bat

echo 기본 패키지 설치...
pip install --no-index --find-links packages pandas numpy regex tqdm requests

echo GLiNER 패키지 설치...
pip install --no-index --find-links packages torch transformers huggingface_hub safetensors tokenizers filelock gliner

echo spaCy 패키지 설치...
pip install --no-index --find-links packages spacy spacy-legacy spacy-loggers murmurhash cymem preshed thinc wasabi srsly catalogue
pip install --no-index --find-links packages ko_core_news_sm-3.8.0-py3-none-any.whl

echo 형태소 분석기 설치 (선택사항)...
pip install --no-index --find-links packages konlpy eunjeon soynlp

echo 설치 완료!
echo GLiNER 모델 파일을 수동으로 캐시 디렉토리에 복사해야 합니다.
echo 캐시 디렉토리: %%USERPROFILE%%\\.cache\\huggingface\\hub\\models--taeminlee--gliner_ko
pause
""")
    
    # Linux/Mac 설치 스크립트
    linux_script = scripts_dir / "install_linux.sh"
    with open(linux_script, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
echo "폐쇄망 환경 오프라인 설치 스크립트 (Linux/Mac)"
echo "=============================================="

echo "가상환경 생성..."
python3 -m venv venv
source venv/bin/activate

echo "기본 패키지 설치..."
pip install --no-index --find-links packages pandas numpy regex tqdm requests

echo "GLiNER 패키지 설치..."
pip install --no-index --find-links packages torch transformers huggingface_hub safetensors tokenizers filelock gliner

echo "spaCy 패키지 설치..."
pip install --no-index --find-links packages spacy spacy-legacy spacy-loggers murmurhash cymem preshed thinc wasabi srsly catalogue
pip install --no-index --find-links packages ko_core_news_sm-3.8.0-py3-none-any.whl

echo "형태소 분석기 설치 (선택사항)..."
pip install --no-index --find-links packages konlpy eunjeon soynlp

echo "설치 완료!"
echo "GLiNER 모델 파일을 수동으로 캐시 디렉토리에 복사해야 합니다."
echo "캐시 디렉토리: ~/.cache/huggingface/hub/models--taeminlee--gliner_ko"
""")
    
    # 실행 권한 부여 (Linux/Mac)
    try:
        os.chmod(linux_script, 0o755)
    except:
        pass
    
    # README 파일 생성
    readme_file = base_dir / "README_OFFLINE.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("""# 폐쇄망 환경 오프라인 설치 가이드

## 📁 디렉토리 구조
```
offline_packages/
├── packages/          # Python 패키지 (.whl 파일들)
├── models/           # GLiNER 모델 파일들 (수동 다운로드 필요)
├── scripts/          # 설치 스크립트들
└── README_OFFLINE.md # 이 파일
```

## 🚀 설치 방법

### Windows
```cmd
cd offline_packages
scripts\\install_windows.bat
```

### Linux/Mac
```bash
cd offline_packages
chmod +x scripts/install_linux.sh
./scripts/install_linux.sh
```

## 📋 수동 작업 필요

### GLiNER 모델 파일 다운로드
1. https://huggingface.co/taeminlee/gliner_ko 접속
2. "Files and versions" 탭 클릭
3. 다음 파일들을 models/ 폴더에 다운로드:
   - config.json
   - pytorch_model.bin (1.21GB)
   - tokenizer_config.json
   - vocab.txt
   - special_tokens_map.json

### 모델 파일 설치
설치 후 models/ 폴더의 파일들을 다음 위치에 복사:

**Windows:**
```
%USERPROFILE%\\.cache\\huggingface\\hub\\models--taeminlee--gliner_ko\\
```

**Linux/Mac:**
```
~/.cache/huggingface/hub/models--taeminlee--gliner_ko/
```

## ✅ 설치 확인
```python
# 기본 패키지 확인
import pandas, numpy
print("기본 패키지 OK")

# spaCy 확인
import spacy
nlp = spacy.load('ko_core_news_sm')
print("spaCy OK")

# GLiNER 확인
from gliner import GLiNER
model = GLiNER.from_pretrained("taeminlee/gliner_ko")
print("GLiNER OK")
```
""")
    
    print(f"✅ 설치 스크립트 생성 완료:")
    print(f"  - Windows: {windows_script}")
    print(f"  - Linux/Mac: {linux_script}")
    print(f"  - README: {readme_file}")
    
    # 8. 요약 정보
    print(f"\n🎉 오프라인 패키지 생성 완료!")
    print(f"📁 생성된 디렉토리: {base_dir.absolute()}")
    print(f"📦 패키지 파일들: {len(list(packages_dir.glob('*.whl')))}개")
    
    print(f"\n📋 다음 단계:")
    print(f"1. {models_dir} 폴더에 GLiNER 모델 파일들을 수동 다운로드")
    print(f"2. {base_dir} 폴더 전체를 폐쇄망으로 복사")
    print(f"3. 폐쇄망에서 해당 설치 스크립트 실행")
    
    return base_dir

if __name__ == "__main__":
    try:
        result_dir = create_offline_packages()
        print(f"\n✅ 성공적으로 완료되었습니다!")
        print(f"결과 디렉토리: {result_dir}")
    except KeyboardInterrupt:
        print(f"\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)