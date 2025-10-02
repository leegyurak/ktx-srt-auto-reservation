@echo off
REM KTX/SRT Macro Windows 빌드 스크립트

echo === KTX/SRT Macro 빌드 시작 (Windows) ===

REM PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
)

REM 이전 빌드 결과 삭제
echo 이전 빌드 결과 삭제 중...
if exist build\windows rmdir /s /q build\windows
if exist build\temp rmdir /s /q build\temp
if exist dist rmdir /s /q dist

REM PyInstaller로 빌드
echo PyInstaller로 빌드 중...
pyinstaller --distpath build\windows --workpath build\temp build.spec

REM 빌드 결과 확인
if exist build\windows\KTX-SRT-Macro.exe (
    echo === 빌드 성공! ===
    echo 빌드된 파일 위치: build\windows\
    dir build\windows\
) else (
    echo === 빌드 실패 ===
    exit /b 1
)
