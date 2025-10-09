# Test Suite

KTX/SRT Macro 프로젝트의 종합 테스트 스위트입니다.

## 📁 테스트 구조

```
tests/
├── unit/                           # 단위 테스트 (빠른 실행, 격리됨)
│   ├── domain/                    # 도메인 모델 테스트
│   │   ├── test_entities.py      # 엔티티 테스트
│   │   ├── test_enums.py         # Enum 테스트
│   │   └── test_train_service.py # 추상 서비스 인터페이스 테스트
│   ├── infrastructure/            # 인프라 레이어 테스트
│   │   └── test_passenger_mapper.py # 승객 매퍼 테스트
│   └── presentation/              # 프레젠테이션 레이어 테스트
│       └── test_qt_components.py # Qt 컴포넌트 테스트
├── integration/                   # 통합 테스트
│   └── infrastructure/
│       ├── test_ktx_service.py   # KTX 서비스 통합 테스트
│       ├── test_srt_service.py   # SRT 서비스 통합 테스트
│       └── test_adapters.py      # 어댑터 통합 테스트
├── conftest.py                    # 공통 픽스처 및 설정
└── README.md                      # 본 문서
```

## 🚀 테스트 실행 (uv 환경)

### 의존성 설치
```bash
# uv를 사용하여 개발 의존성 설치
uv pip install -e ".[dev]"
```

### 기본 실행
```bash
# 전체 테스트 실행
pytest

# 단위 테스트만 실행
pytest -m unit

# 통합 테스트만 실행
pytest -m integration

# 특정 레이어 테스트
pytest -m domain          # 도메인 레이어만
pytest -m mapper          # 매퍼만
pytest -m service         # 서비스 레이어만
pytest -m ui              # UI 레이어만
```

### 특정 파일/클래스/메서드 실행
```bash
# 특정 파일
pytest tests/unit/infrastructure/test_passenger_mapper.py

# 특정 클래스
pytest tests/unit/infrastructure/test_passenger_mapper.py::TestPassengerMapperToKorail

# 특정 메서드
pytest tests/unit/infrastructure/test_passenger_mapper.py::TestPassengerMapperToKorail::test_convert_adult_passenger_to_korail
```

### 커버리지 리포트
```bash
# 터미널에 커버리지 출력 (누락된 라인 표시)
pytest --cov=src --cov-report=term-missing

# HTML 리포트 생성
pytest --cov=src --cov-report=html

# HTML 리포트 열기
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 고급 실행 옵션
```bash
# 자세한 출력
pytest -v

# 매우 자세한 출력 (print 문 포함)
pytest -vv -s

# 실패 시 즉시 중지
pytest -x

# 처음 3개 실패 후 중지
pytest --maxfail=3

# 병렬 실행 (pytest-xdist 필요)
pytest -n auto

# 느린 테스트 제외
pytest -m "not slow"

# 특정 키워드 매칭
pytest -k "mapper"
```

## 📝 테스트 작성 가이드

### AAA 패턴 사용
모든 테스트는 Arrange-Act-Assert 패턴을 따릅니다:

```python
def test_example():
    # Arrange: 테스트 데이터 및 조건 준비
    passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)

    # Act: 테스트할 동작 실행
    result = PassengerMapper.to_korail(passenger)

    # Assert: 결과 검증
    assert isinstance(result, AdultPassenger)
    assert result.count == 2
```

### 픽스처 활용
공통 테스트 데이터는 `conftest.py`의 픽스처를 사용:

```python
def test_with_fixture(adult_passenger, sample_train_schedule):
    # 픽스처가 자동으로 주입됨
    assert adult_passenger.count == 2
    assert sample_train_schedule.train_number == "001"
```

### 마커 사용
테스트에 적절한 마커를 추가:

```python
@pytest.mark.unit
@pytest.mark.domain
class TestPassenger:
    def test_create_passenger(self):
        ...

@pytest.mark.integration
@pytest.mark.slow
class TestKTXService:
    def test_full_reservation_flow(self):
        ...
```

## 🏷️ 사용 가능한 마커

| 마커 | 설명 | 용도 |
|------|------|------|
| `unit` | 단위 테스트 | 빠른 실행, 격리된 테스트 |
| `integration` | 통합 테스트 | 컴포넌트 간 상호작용 테스트 |
| `domain` | 도메인 레이어 | 비즈니스 로직 테스트 |
| `mapper` | 매퍼 | 데이터 변환 테스트 |
| `service` | 서비스 레이어 | 서비스 로직 테스트 |
| `ui` | UI/Presentation | Qt 컴포넌트 테스트 |
| `slow` | 느린 테스트 | 시간이 오래 걸리는 테스트 |

## 🎯 커버리지 목표

| 레이어 | 목표 커버리지 |
|--------|--------------|
| 전체 | 70% 이상 |
| 도메인 레이어 | 90% 이상 |
| 매퍼 | 100% |
| 인프라 레이어 | 70% 이상 |
| 프레젠테이션 | 50% 이상 (UI 테스트 특성상) |

## 🔧 CI/CD 통합

### GitHub Actions 예시
```yaml
- name: Run tests
  run: |
    uv pip install -e ".[dev]"
    pytest --cov=src --cov-report=xml --cov-fail-under=70
```

## 📚 추가 리소스

- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest-qt 문서](https://pytest-qt.readthedocs.io/)
- [Coverage.py 문서](https://coverage.readthedocs.io/)
