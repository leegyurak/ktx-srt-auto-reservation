# 🚄 기차표 자동 예약 프로그램

KTX/ITX와 SRT 기차표를 자동으로 예약하는 크로스 플랫폼 GUI 애플리케이션입니다.

## ✨ 주요 기능

- **🚄 KTX/ITX 예약**: 코레일 시스템을 통한 자동 예약
- **🚅 SRT 예약**: SRT 시스템을 통한 자동 예약
- **💻 크로스 플랫폼**: Windows, macOS, Linux 지원
- **🎨 현대적 UI**: Flet 기반의 깔끔한 사용자 인터페이스
- **📊 실시간 로그**: 예약 진행 상황 실시간 모니터링
- **💳 자동 결제**: 카드 정보 입력 시 자동 결제
- **⏹️ 안전한 중지**: 언제든지 예약 과정 중단 가능

## 🚀 실행 방법

### 개발 환경에서 실행

```bash
# uv 환경에서 실행 (권장)
uv run python run.py

# 또는 직접 실행
python run.py
```

### 플랫폼별 실행

**Windows:**
```cmd
build\run.bat
```

**macOS/Linux:**
```bash
./build/run.sh
```

## 📦 독립 실행 파일 빌드

### 자동 빌드

**Windows:**
```cmd
build\build.bat
```

**macOS/Linux:**
```bash
./build/build.sh
```

**Python 스크립트:**
```bash
cd build
python build.py
```

### 수동 빌드

**Flet Pack 사용 (권장):**
```bash
# 의존성 설치
pip install "flet[desktop]"

# 빌드 실행
flet pack src/flet_app.py \
    --name "기차표자동예약" \
    --description "KTX/SRT 기차표 자동 예약 프로그램" \
    --product-name "Train Reservation" \
    --product-version "1.0.0" \
    --add-data "src/srt.py:." \
    --add-data "src/ktx.py:."
```

**PyInstaller 사용 (대안):**
```bash
# 의존성 설치
pip install pyinstaller

# 빌드 실행
pyinstaller --onefile --windowed \
    --name "TrainReservation" \
    --add-data "src/srt.py:." \
    --add-data "src/ktx.py:." \
    src/flet_app.py
```

## 📁 프로젝트 구조

```
srtmacro/
├── src/                 # 소스 코드
│   ├── flet_app.py      # 메인 GUI 애플리케이션
│   ├── srt.py           # SRT 예약 모듈
│   └── ktx.py           # KTX 예약 모듈
├── build/               # 빌드 스크립트
│   ├── build.py         # Python 빌드 스크립트
│   ├── build.sh         # macOS/Linux 빌드 스크립트
│   ├── build.bat        # Windows 빌드 스크립트
│   ├── run.sh           # macOS/Linux 실행 스크립트
│   └── run.bat          # Windows 실행 스크립트
├── run.py               # 메인 런처
├── pyproject.toml       # 프로젝트 설정 및 의존성
├── requirements.txt     # pip 의존성 파일
└── README.md            # 이 파일
```

## 🔧 의존성

- Python 3.10+
- flet[desktop] >= 0.21.0
- requests >= 2.32.5
- cryptography >= 46.0.1
- curl-cffi >= 0.13.0
- pycryptodome >= 3.18.0

## 📖 사용법

1. **프로그램 실행**: 위의 실행 방법 중 하나를 선택하여 실행
2. **탭 선택**: KTX/ITX 또는 SRT 탭 선택
3. **로그인 정보 입력**: 각 시스템의 로그인 정보 입력
4. **검색 조건 설정**: 출발역, 도착역, 날짜, 시간 설정
5. **결제 정보 입력** (선택사항): 자동 결제를 원할 경우 카드 정보 입력
6. **예약 시작**: "예약 시작" 버튼 클릭
7. **진행 상황 확인**: 실시간 로그에서 예약 진행 상황 확인

## 🔐 보안 주의사항

- 로그인 정보와 카드 정보는 로컬에 저장되지 않습니다
- 프로그램 종료 시 모든 정보가 삭제됩니다
- 개인정보 보호를 위해 공용 컴퓨터에서 사용 시 주의하세요

## 🐛 문제 해결

### 실행 오류
- Python 3.10 이상이 설치되어 있는지 확인
- 필요한 의존성이 설치되어 있는지 확인: `pip install -r requirements.txt`

### 빌드 오류
- Flet pack 실패 시 PyInstaller 사용
- 가상환경에서 빌드 시도

### 로그인 오류
- 로그인 정보가 정확한지 확인
- 네트워크 연결 상태 확인
- 해당 사이트에서 직접 로그인이 가능한지 확인

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

## ⚠️ 면책사항

이 프로그램은 교육 및 개인 사용 목적으로 제작되었습니다. 사용자는 해당 서비스의 이용약관을 준수해야 하며, 프로그램 사용으로 인한 모든 책임은 사용자에게 있습니다.