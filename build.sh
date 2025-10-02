#!/bin/bash

# KTX/SRT Macro 빌드 스크립트 (macOS)

echo "=== KTX/SRT Macro 빌드 시작 (macOS) ==="

# 가상환경 활성화 (필요시)
# source venv/bin/activate

# Python과 pip 확인
if ! command -v python3 &> /dev/null
then
    echo "Python3가 설치되어 있지 않습니다."
    exit 1
fi

# PyInstaller 설치 확인
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller가 설치되어 있지 않습니다. 설치 중..."
    python3 -m pip install pyinstaller
fi

# 이전 빌드 결과 삭제
echo "이전 빌드 결과 삭제 중..."
rm -rf build/mac build/temp dist

# PyInstaller로 빌드
echo "PyInstaller로 빌드 중..."
pyinstaller --distpath build/mac --workpath build/temp build.spec

# 빌드 결과 확인
if [ -f "build/mac/KTX-SRT-Macro" ] || [ -d "build/mac/KTX-SRT-Macro.app" ]; then
    echo "=== 빌드 성공! ==="
    echo "빌드된 파일 위치: build/mac/"
    ls -lh build/mac/
else
    echo "=== 빌드 실패 ==="
    exit 1
fi
