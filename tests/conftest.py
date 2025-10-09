"""Pytest configuration and shared fixtures for all tests"""
import sys
import os
import pytest
from datetime import datetime, date

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.domain.models.entities import (
    Passenger, TrainSchedule, ReservationRequest,
    ReservationResult, CreditCard, PaymentResult, Station
)
from src.domain.models.enums import PassengerType, TrainType


# ===== Domain Model Fixtures =====

@pytest.fixture
def adult_passenger():
    """Fixture for adult passenger"""
    return Passenger(passenger_type=PassengerType.ADULT, count=2)


@pytest.fixture
def child_passenger():
    """Fixture for child passenger"""
    return Passenger(passenger_type=PassengerType.CHILD, count=1)


@pytest.fixture
def senior_passenger():
    """Fixture for senior passenger"""
    return Passenger(passenger_type=PassengerType.SENIOR, count=1)


@pytest.fixture
def passengers_list():
    """Fixture for list of passengers"""
    return [
        Passenger(passenger_type=PassengerType.ADULT, count=2),
        Passenger(passenger_type=PassengerType.CHILD, count=1),
    ]


@pytest.fixture
def sample_station_seoul():
    """Fixture for Seoul station"""
    return Station(name="서울", code="0001")


@pytest.fixture
def sample_station_busan():
    """Fixture for Busan station"""
    return Station(name="부산", code="0002")


@pytest.fixture
def sample_train_schedule():
    """Fixture for train schedule"""
    return TrainSchedule(
        train_number="001",
        departure_station="서울",
        arrival_station="부산",
        departure_time=datetime(2025, 1, 15, 10, 0, 0),
        arrival_time=datetime(2025, 1, 15, 12, 30, 0),
        train_type=TrainType.KTX,
        available_seats=10,
        price=59800
    )


@pytest.fixture
def sample_srt_train_schedule():
    """Fixture for SRT train schedule"""
    return TrainSchedule(
        train_number="S001",
        departure_station="수서",
        arrival_station="부산",
        departure_time=datetime(2025, 1, 15, 10, 0, 0),
        arrival_time=datetime(2025, 1, 15, 12, 30, 0),
        train_type=TrainType.SRT,
        available_seats=10,
        price=52000
    )


@pytest.fixture
def sample_reservation_request():
    """Fixture for reservation request"""
    return ReservationRequest(
        departure_station="서울",
        arrival_station="부산",
        departure_date=date(2025, 1, 15),
        departure_time="100000",
        passengers=[
            Passenger(passenger_type=PassengerType.ADULT, count=2),
            Passenger(passenger_type=PassengerType.CHILD, count=1)
        ],
        train_type=TrainType.KTX
    )


@pytest.fixture
def sample_srt_reservation_request():
    """Fixture for SRT reservation request"""
    return ReservationRequest(
        departure_station="수서",
        arrival_station="부산",
        departure_date=date(2025, 1, 15),
        departure_time="100000",
        passengers=[
            Passenger(passenger_type=PassengerType.ADULT, count=2),
        ],
        train_type=TrainType.SRT
    )


@pytest.fixture
def successful_reservation_result(sample_train_schedule):
    """Fixture for successful reservation result"""
    return ReservationResult(
        success=True,
        reservation_number="R123456",
        message="Reservation successful",
        train_schedule=sample_train_schedule
    )


@pytest.fixture
def failed_reservation_result():
    """Fixture for failed reservation result"""
    return ReservationResult(
        success=False,
        message="No seats available"
    )


@pytest.fixture
def personal_credit_card():
    """Fixture for personal credit card"""
    return CreditCard(
        number="1234567812345678",
        password="12",
        validation_number="990101",
        expire="2512",
        is_corporate=False
    )


@pytest.fixture
def corporate_credit_card():
    """Fixture for corporate credit card"""
    return CreditCard(
        number="1234567812345678",
        password="12",
        validation_number="1234567890",
        expire="2512",
        is_corporate=True
    )


@pytest.fixture
def successful_payment_result():
    """Fixture for successful payment result"""
    return PaymentResult(
        success=True,
        message="Payment successful",
        reservation_number="R123456"
    )


@pytest.fixture
def failed_payment_result():
    """Fixture for failed payment result"""
    return PaymentResult(
        success=False,
        message="Payment failed"
    )


# ===== Service Mock Fixtures =====

@pytest.fixture
def mock_korail_train():
    """Fixture for mock Korail train object"""
    from unittest.mock import Mock
    train = Mock()
    train.train_no = "001"
    train.dep_date = "20250115"
    train.dep_time = "100000"
    train.arr_date = "20250115"
    train.arr_time = "123000"
    train.train_type = "KTX"
    train.adultcharge = "59800"
    train.seat_count = 10
    train.has_seat.return_value = True
    return train


@pytest.fixture
def mock_srt_train():
    """Fixture for mock SRT train object"""
    from unittest.mock import Mock
    train = Mock()
    train.train_number = "S001"
    train.dep_date = "20250115"
    train.dep_time = "100000"
    train.arr_date = "20250115"
    train.arr_time = "123000"
    train.adultcharge = "52000"
    train.seat_count = 10
    train.seat_available.return_value = True
    return train


@pytest.fixture
def mock_korail_reservation():
    """Fixture for mock Korail reservation"""
    from unittest.mock import Mock
    reservation = Mock()
    reservation.rsv_id = "R123456"
    return reservation


@pytest.fixture
def mock_srt_reservation():
    """Fixture for mock SRT reservation"""
    from unittest.mock import Mock
    reservation = Mock()
    reservation.reservation_number = "R123456"
    return reservation


# ===== Test Configuration =====

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "ui: UI/Presentation layer tests")
    config.addinivalue_line("markers", "mapper: Mapper tests")
    config.addinivalue_line("markers", "service: Service layer tests")
    config.addinivalue_line("markers", "domain: Domain model tests")
