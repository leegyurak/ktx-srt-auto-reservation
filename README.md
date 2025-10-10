<div align="center">

# 🚄 KTX/SRT 기차표 자동 예약 매크로

**빠르고 편리한 기차표 예약을 위한 스마트 솔루션**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=for-the-badge)](https://github.com/astral-sh/uv)
[![Tests](https://img.shields.io/github/actions/workflow/status/leegyurak/ktx-srt-macro/test.yml?branch=main&style=for-the-badge&label=Tests)](https://github.com/leegyurak/ktx-srt-macro/actions/workflows/test.yml)
[![codecov](https://img.shields.io/codecov/c/github/leegurak/ktx-srt-macro?style=for-the-badge&logo=codecov&logoColor=white)](https://codecov.io/gh/leegyurak/ktx-srt-macro)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

</div>

## 📖 소개

KTX/SRT 기차표 자동 예약 매크로는 코레일(KTX)과 SRT의 온라인 예약 시스템을 자동화하여,
원하는 열차표를 빠르고 정확하게 예약할 수 있도록 도와주는 데스크톱 애플리케이션입니다.

특히 명절이나 주말 같은 성수기에 원하는 시간대의 표를 구하기 어려운 상황에서,
자동으로 반복 검색하여 예약 가능한 좌석을 찾아주는 기능을 제공합니다.

## ✨ 주요 기능

### 🚄 통합 예약 시스템
- **KTX 자동 예약**: 코레일 시스템 완벽 지원
- **SRT 자동 예약**: SRT 시스템 완벽 지원
- **동시 다중 검색**: 여러 시간대의 열차를 동시에 모니터링

### 🎯 스마트 예약
- **실시간 좌석 확인**: 0.1초 단위의 빠른 좌석 검색
- **자동 재시도**: 예약 실패 시 자동으로 재시도
- **우선순위 설정**: 선호하는 열차 종류 및 좌석 타입 지정
- **시간대 범위 설정**: 출발/도착 시간 범위 내에서 자동 검색

### 💳 편리한 결제
- **자동 결제 지원**: 카드 정보 입력 시 예약 후 자동 결제
- **보안 자격 증명 저장**: 로그인 정보와 결제 정보를 안전하게 저장 (선택사항)
  - **macOS**: Keychain에 암호화 저장
  - **Windows**: Windows Credential Locker에 암호화 저장
  - **Linux**: Secret Service API에 암호화 저장
- **결제 확인**: 결제 전 최종 확인 단계 제공

### 🎨 사용자 친화적 인터페이스
- **직관적인 GUI**: PyQt6 기반의 깔끔하고 현대적인 디자인
- **실시간 로그**: 예약 진행 상황을 실시간으로 확인
- **다크 모드**: 눈의 피로를 줄이는 다크 모드 지원
- **크로스 플랫폼**: Windows와 macOS 모두 지원

### 🔒 보안 및 안정성
- **플랫폼 네이티브 보안 저장소**: OS의 보안 저장소를 활용한 자격 증명 관리
  - macOS Keychain, Windows Credential Locker, Linux Secret Service 지원
- **암호화 통신**: 모든 개인정보는 암호화되어 전송
- **세션 관리**: 안전한 로그인 세션 유지
- **에러 핸들링**: 예외 상황에 대한 철저한 처리
- **안전한 종료**: 언제든지 안전하게 프로세스 중단 가능

## 🚀 빠른 시작

### 📥 다운로드

#### 방법 1: 실행 파일 다운로드 (권장)

가장 간단한 방법입니다. 별도의 설치 없이 바로 실행할 수 있습니다.

1. [Releases](../../releases) 페이지에서 최신 버전 다운로드
2. Windows: `KTX-SRT-Macro.exe` 실행
3. macOS: `KTX-SRT-Macro.app` 실행

#### 방법 2: 소스 코드에서 실행

개발 환경이 구축되어 있거나 소스 코드를 수정하고 싶은 경우 사용합니다.

**사전 요구사항**
- Python 3.10 이상
- [uv](https://docs.astral.sh/uv/) 패키지 매니저

**1. uv 설치**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. 프로젝트 설정 및 실행**

```bash
# 저장소 클론
git clone https://github.com/yourusername/ktx-srt-macro.git
cd ktx-srt-macro

# 의존성 자동 설치 및 프로그램 실행
uv run python main.py
```

> 💡 **Tip**: `uv run` 명령어는 필요한 모든 의존성을 자동으로 설치하고 프로그램을 실행합니다.

## 📖 사용 방법

### 1️⃣ 프로그램 실행 및 로그인

<table>
<tr>
<td width="50%">

**KTX/ITX 예약**

1. KTX 탭 선택
2. 코레일 회원 아이디/비밀번호 입력
3. "로그인 정보 저장" 체크 (선택사항)
4. "열차 검색" 버튼 클릭

</td>
<td width="50%">

**SRT 예약**

1. SRT 탭 선택
2. SRT 회원 아이디/비밀번호 입력
3. "로그인 정보 저장" 체크 (선택사항)
4. "열차 검색" 버튼 클릭

</td>
</tr>
</table>

> 💡 **Tip**: "로그인 정보 저장"을 체크하면 다음 실행 시 자동으로 로그인 정보가 입력됩니다. 모든 정보는 OS의 보안 저장소에 암호화되어 저장됩니다.

### 2️⃣ 검색 조건 설정

```
📍 출발역: 서울
📍 도착역: 부산
📅 날짜: 2025-10-10
⏰ 시간: 09:00 ~ 12:00
💺 좌석: 일반실
```

### 3️⃣ 결제 정보 입력 (선택사항)

자동 결제를 원할 경우:
- 카드번호 (16자리)
- 카드 비밀번호 앞 2자리
- 유효기간 (YYMM)
- 생년월일 (YYMMDD) 또는 사업자등록번호 (10자리)
- "결제 정보 저장" 체크 (선택사항)

> 🔐 **보안 안내**:
> - "결제 정보 저장"을 체크하면 운영체제의 보안 저장소에 암호화되어 저장됩니다
> - macOS는 Keychain, Windows는 Credential Locker를 사용합니다
> - 평문으로 파일에 저장되지 않으며, 다른 앱에서 접근할 수 없습니다

### 4️⃣ 예약 시작

1. "예약 시작" 버튼 클릭
2. 실시간 로그에서 진행 상황 확인
3. 좌석 발견 시 자동 예약 진행
4. 결제 정보 입력 시 자동 결제 완료

### 5️⃣ 예약 완료

```
✅ 예약 성공!
🎫 열차: KTX-101
🕐 출발: 09:00
📍 경로: 서울 → 부산
💺 좌석: 3호차 12A
```

## 🛠️ 개발자 가이드

### 🧪 테스트 실행

프로젝트는 포괄적인 테스트 스위트를 포함하고 있습니다.

```bash
# 모든 테스트 실행
uv run pytest tests/ -v

# 테스트 커버리지 포함
uv run pytest tests/ -v --cov=src --cov-report=html

# 특정 테스트만 실행
uv run pytest tests/unit/ -v                    # 단위 테스트만
uv run pytest tests/integration/ -v             # 통합 테스트만
uv run pytest tests/ -k "external" -v           # 외부 모듈 테스트만
```

커버리지 리포트는 `htmlcov/index.html`에서 확인할 수 있습니다.

**CI/CD**: 모든 Push와 Pull Request에 대해 자동으로 테스트가 실행됩니다.
- 3개 OS (Ubuntu, Windows, macOS)
- 3개 Python 버전 (3.11, 3.12, 3.13)
- 총 9개 조합에서 테스트

### 📦 독립 실행 파일 빌드

#### 로컬에서 빌드

**Windows**
```bash
# 의존성 설치
uv sync

# 빌드 실행
uv run pyinstaller --name KTX-SRT-Macro --onefile --windowed \
  --icon "assets/favicon.ico" --add-data "src;src" --add-data "assets;assets" \
  --noupx main.py
```

**macOS**
```bash
# 의존성 설치
uv sync

# 빌드 실행
uv run pyinstaller --name KTX-SRT-Macro --onefile --windowed \
  --icon "assets/favicon.icns" --add-data "src:src" --add-data "assets:assets" main.py
```

빌드된 실행 파일은 `dist/` 디렉토리에 생성됩니다.

#### GitHub Actions 자동 빌드

태그를 푸시하면 자동으로 Windows와 macOS용 실행 파일을 빌드하고 릴리스를 생성합니다:

```bash
# 새 버전 태그 생성
git tag v1.0.0

# 태그 푸시
git push origin v1.0.0

# GitHub Actions가 자동으로:
# 1. Windows/macOS 빌드 실행
# 2. 릴리스 생성
# 3. 실행 파일 업로드
```

### 📁 프로젝트 구조

프로젝트는 **클린 아키텍처** 원칙에 따라 구성되어 있습니다:

```
ktx-srt-macro/
│
├── 📂 src/                          # 소스 코드 루트
│   │
│   ├── 📂 constants/                # 상수 및 설정
│   │   ├── __init__.py
│   │   ├── stations.py              # 기차역 정보
│   │   └── ui.py                    # UI 관련 상수
│   │
│   ├── 📂 domain/                   # 도메인 레이어 (비즈니스 로직)
│   │   ├── 📂 models/               # 도메인 모델
│   │   │   ├── entities.py          # 핵심 엔티티 (Train, Passenger 등)
│   │   │   └── enums.py             # 열거형 (TrainType, SeatType 등)
│   │   └── 📂 services/             # 도메인 서비스
│   │       └── train_service.py     # 기차 예약 비즈니스 로직
│   │
│   ├── 📂 infrastructure/           # 인프라스트럭처 레이어
│   │   ├── 📂 adapters/             # 외부 서비스 어댑터
│   │   │   ├── ktx_service.py       # KTX 서비스 어댑터
│   │   │   └── srt_service.py       # SRT 서비스 어댑터
│   │   ├── 📂 external/             # 외부 API 클라이언트
│   │   │   ├── ktx.py               # 코레일 API 클라이언트
│   │   │   └── srt.py               # SRT API 클라이언트
│   │   └── 📂 security/             # 보안 인프라
│   │       ├── credential_storage.py # 자격 증명 저장소 (DAO)
│   │       └── dto.py               # 보안 DTO
│   │
│   └── 📂 presentation/             # 프레젠테이션 레이어 (UI)
│       └── qt.py                    # PyQt6 GUI 애플리케이션
│
├── 📂 assets/                       # 리소스 파일
│   ├── favicon.ico                  # Windows 아이콘
│   └── favicon.icns                 # macOS 아이콘
│
├── 📂 .github/                      # GitHub 설정
│   └── 📂 workflows/                # CI/CD 파이프라인
│       └── build.yml                # 자동 빌드 워크플로우
│
├── 📄 main.py                       # 애플리케이션 진입점
├── 📄 pyproject.toml                # 프로젝트 메타데이터 및 의존성
├── 📄 .gitignore                    # Git 제외 파일
└── 📄 README.md                     # 프로젝트 문서
```

### 🔧 기술 스택

<table>
<tr>
<td width="50%">

**Core**
- ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white) 프로그래밍 언어
- ![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?logo=qt&logoColor=white) GUI 프레임워크
- ![uv](https://img.shields.io/badge/uv-DE5FE9) 패키지 매니저

</td>
<td width="50%">

**Libraries**
- `requests` - HTTP 클라이언트
- `curl-cffi` - TLS 지문 우회
- `cryptography` - 암호화
- `pycryptodome` - 추가 암호화 기능
- `keyring` - 플랫폼 보안 저장소

</td>
</tr>
<tr>
<td width="50%">

**Build & Deploy**
- `PyInstaller` - 실행 파일 빌드
- `GitHub Actions` - CI/CD 자동화

</td>
<td width="50%">

**Architecture**
- Clean Architecture
- Domain-Driven Design
- Repository Pattern

</td>
</tr>
</table>

## 🔐 보안 및 개인정보 보호

### 🛡️ 보안 정책

- **플랫폼 네이티브 보안 저장소**:
  - macOS의 Keychain, Windows의 Credential Locker, Linux의 Secret Service API 사용
  - 운영체제 수준의 암호화로 자격 증명 보호
  - 다른 애플리케이션의 접근 차단
- **암호화 전송**: 모든 개인정보는 HTTPS를 통해 암호화되어 전송됩니다
- **파일 저장 없음**: 자격 증명을 평문 파일로 저장하지 않습니다
- **선택적 저장**: "정보 저장" 옵션을 해제하면 정보가 저장되지 않습니다
- **세션 보안**: 안전한 세션 관리를 통해 무단 액세스를 방지합니다

### 🔒 보안 저장소 작동 방식

1. **저장 시**: "정보 저장"을 체크하면 OS의 보안 저장소에 암호화되어 저장
2. **불러오기**: 다음 실행 시 보안 저장소에서 자동으로 복호화하여 로드
3. **삭제**: "정보 저장" 체크 해제 후 로그인하면 보안 저장소에서 삭제

### ⚠️ 주의사항

- 공용 컴퓨터에서는 "정보 저장" 옵션을 사용하지 마세요
- 프로그램 사용 후 반드시 로그아웃하세요
- 의심스러운 예약 내역은 즉시 해당 사이트에서 확인하세요
- 자격 증명을 삭제하려면 체크박스를 해제하고 다시 로그인하세요

## ❓ FAQ (자주 묻는 질문)

<details>
<summary><b>Q1. 예약이 실패하는 이유는 무엇인가요?</b></summary>

- 좌석이 매진되었을 수 있습니다
- 로그인 세션이 만료되었을 수 있습니다 (재로그인 필요)
- 네트워크 연결이 불안정할 수 있습니다
- 입력한 정보가 잘못되었을 수 있습니다

</details>

<details>
<summary><b>Q2. 카드 정보를 입력하지 않아도 되나요?</b></summary>

네, 카드 정보는 선택사항입니다. 입력하지 않으면 예약까지만 진행되고, 사용자가 직접 해당 사이트에서 결제를 완료할 수 있습니다.

</details>

<details>
<summary><b>Q3. 여러 시간대를 동시에 검색할 수 있나요?</b></summary>

현재 버전에서는 지정된 시간 범위 내의 모든 열차를 순차적으로 검색합니다. 원하는 시간대를 범위로 설정하면 해당 범위 내에서 가장 빠르게 예약 가능한 좌석을 찾습니다.

</details>

<details>
<summary><b>Q4. 프로그램이 실행되지 않아요.</b></summary>

**Windows**: Windows Defender나 백신 프로그램이 차단할 수 있습니다. 신뢰할 수 있는 앱으로 추가하세요.

**macOS**: "확인되지 않은 개발자" 오류 발생 시:
1. 시스템 환경설정 > 보안 및 개인정보 보호
2. "확인 없이 열기" 클릭

</details>

<details>
<summary><b>Q5. 예약 속도를 더 빠르게 할 수 있나요?</b></summary>

프로그램은 이미 최적화된 검색 주기를 사용합니다. 너무 빠른 요청은 서버 측에서 차단될 수 있어 적절한 간격으로 요청을 보냅니다.

</details>

<details>
<summary><b>Q6. 저장된 정보는 안전한가요?</b></summary>

네, 매우 안전합니다:
- **macOS**: Keychain에 저장 (Mac 비밀번호로 보호)
- **Windows**: Credential Locker에 저장 (Windows 계정으로 보호)
- **Linux**: Secret Service API에 저장 (시스템 암호화)

모든 정보는 운영체제 수준에서 암호화되며, 다른 앱에서 접근할 수 없습니다. 평문 파일로 저장되지 않습니다.

</details>

<details>
<summary><b>Q7. 저장된 정보를 삭제하려면 어떻게 하나요?</b></summary>

1. 각 섹션의 "정보 저장" 체크박스를 해제
2. 로그인 또는 예약 진행
3. 체크박스가 해제된 상태에서 저장소의 정보가 자동으로 삭제됩니다

또는 운영체제의 보안 저장소에서 직접 삭제할 수 있습니다:
- **macOS**: Keychain Access 앱에서 "KTX-SRT-Macro" 항목 삭제
- **Windows**: 자격 증명 관리자에서 "KTX-SRT-Macro" 항목 삭제

</details>

## 🐛 문제 해결

### 일반적인 오류

| 문제 | 해결 방법 |
|------|----------|
| 로그인 실패 | 아이디/비밀번호 확인, 해당 사이트에서 직접 로그인 테스트 |
| 네트워크 오류 | 인터넷 연결 확인, 방화벽 설정 확인 |
| 세션 만료 | 프로그램 재시작 후 다시 로그인 |
| 결제 실패 | 카드 정보 재확인, 카드사 승인 상태 확인 |

### 로그 확인

문제 발생 시 실시간 로그 창에 표시되는 오류 메시지를 확인하세요. 대부분의 문제는 로그를 통해 원인을 파악할 수 있습니다.

## 🤝 기여하기

프로젝트에 기여하고 싶으신가요? 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

### 오픈소스 라이선스 고지

이 프로젝트는 다음 오픈소스 프로젝트의 코드를 포함하고 있습니다:

- **[SRT](https://github.com/ryanking13/SRT)** by ryanking13 - MIT License
- **[korail2](https://github.com/carpedm20/korail2)** by carpedm20 - BSD License

각 라이선스의 전문은 해당 프로젝트의 저장소에서 확인할 수 있습니다.

## ⚠️ 면책사항

```
이 프로그램은 교육 및 개인 사용 목적으로 제작되었습니다.

- 사용자는 코레일 및 SRT의 이용약관을 준수해야 합니다
- 프로그램 사용으로 인한 모든 책임은 사용자에게 있습니다
- 상업적 목적의 사용은 금지됩니다
- 과도한 사용은 서비스 제공자의 정책에 위배될 수 있습니다
```

## 📞 문의

프로젝트 관련 문의사항이 있으시면 [Issues](../../issues) 페이지를 이용해주세요.

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요! ⭐**

Made with ❤️ by developers, for travelers

</div>