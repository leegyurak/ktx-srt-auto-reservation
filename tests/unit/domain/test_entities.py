"""Unit tests for domain entities"""
import pytest
from datetime import datetime, date
from src.domain.models.entities import (
    Passenger, Station, TrainSchedule, ReservationRequest,
    ReservationResult, CreditCard, PaymentResult
)
from src.domain.models.enums import PassengerType, TrainType


@pytest.mark.unit
@pytest.mark.domain
class TestPassenger:
    """Tests for Passenger entity"""

    def test_create_adult_passenger(self):
        """Test creating an adult passenger"""
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)
        assert passenger.passenger_type == PassengerType.ADULT
        assert passenger.count == 2

    def test_create_child_passenger(self):
        """Test creating a child passenger"""
        passenger = Passenger(passenger_type=PassengerType.CHILD, count=1)
        assert passenger.passenger_type == PassengerType.CHILD
        assert passenger.count == 1

    def test_create_senior_passenger(self):
        """Test creating a senior passenger"""
        passenger = Passenger(passenger_type=PassengerType.SENIOR, count=1)
        assert passenger.passenger_type == PassengerType.SENIOR
        assert passenger.count == 1


@pytest.mark.unit
@pytest.mark.domain
class TestStation:
    """Tests for Station entity"""

    def test_create_station(self):
        """Test creating a station"""
        station = Station(name="서울", code="0001")
        assert station.name == "서울"
        assert station.code == "0001"


@pytest.mark.unit
@pytest.mark.domain
class TestTrainSchedule:
    """Tests for TrainSchedule entity"""

    def test_create_train_schedule(self):
        """Test creating a train schedule"""
        departure_time = datetime(2025, 1, 15, 10, 0, 0)
        arrival_time = datetime(2025, 1, 15, 12, 30, 0)

        schedule = TrainSchedule(
            train_number="001",
            departure_station="서울",
            arrival_station="부산",
            departure_time=departure_time,
            arrival_time=arrival_time,
            train_type=TrainType.KTX,
            available_seats=10,
            price=59800
        )

        assert schedule.train_number == "001"
        assert schedule.departure_station == "서울"
        assert schedule.arrival_station == "부산"
        assert schedule.departure_time == departure_time
        assert schedule.arrival_time == arrival_time
        assert schedule.train_type == TrainType.KTX
        assert schedule.available_seats == 10
        assert schedule.price == 59800


@pytest.mark.unit
@pytest.mark.domain
class TestReservationRequest:
    """Tests for ReservationRequest entity"""

    def test_create_reservation_request(self):
        """Test creating a reservation request"""
        departure_date = date(2025, 1, 15)
        passengers = [
            Passenger(passenger_type=PassengerType.ADULT, count=2),
            Passenger(passenger_type=PassengerType.CHILD, count=1)
        ]

        request = ReservationRequest(
            departure_station="서울",
            arrival_station="부산",
            departure_date=departure_date,
            departure_time="100000",
            passengers=passengers,
            train_type=TrainType.KTX
        )

        assert request.departure_station == "서울"
        assert request.arrival_station == "부산"
        assert request.departure_date == departure_date
        assert request.departure_time == "100000"
        assert len(request.passengers) == 2
        assert request.train_type == TrainType.KTX


@pytest.mark.unit
@pytest.mark.domain
class TestReservationResult:
    """Tests for ReservationResult entity"""

    def test_create_successful_reservation_result(self):
        """Test creating a successful reservation result"""
        departure_time = datetime(2025, 1, 15, 10, 0, 0)
        arrival_time = datetime(2025, 1, 15, 12, 30, 0)

        schedule = TrainSchedule(
            train_number="001",
            departure_station="서울",
            arrival_station="부산",
            departure_time=departure_time,
            arrival_time=arrival_time,
            train_type=TrainType.KTX,
            available_seats=10,
            price=59800
        )

        result = ReservationResult(
            success=True,
            reservation_number="R123456",
            message="Reservation successful",
            train_schedule=schedule
        )

        assert result.success is True
        assert result.reservation_number == "R123456"
        assert result.message == "Reservation successful"
        assert result.train_schedule == schedule

    def test_create_failed_reservation_result(self):
        """Test creating a failed reservation result"""
        result = ReservationResult(
            success=False,
            message="No seats available"
        )

        assert result.success is False
        assert result.reservation_number is None
        assert result.message == "No seats available"
        assert result.train_schedule is None


@pytest.mark.unit
@pytest.mark.domain
class TestCreditCard:
    """Tests for CreditCard entity"""

    def test_create_personal_credit_card(self):
        """Test creating a personal credit card"""
        card = CreditCard(
            number="1234567812345678",
            password="12",
            validation_number="990101",
            expire="2512",
            is_corporate=False
        )

        assert card.number == "1234567812345678"
        assert card.password == "12"
        assert card.validation_number == "990101"
        assert card.expire == "2512"
        assert card.is_corporate is False

    def test_create_corporate_credit_card(self):
        """Test creating a corporate credit card"""
        card = CreditCard(
            number="1234567812345678",
            password="12",
            validation_number="1234567890",
            expire="2512",
            is_corporate=True
        )

        assert card.number == "1234567812345678"
        assert card.password == "12"
        assert card.validation_number == "1234567890"
        assert card.expire == "2512"
        assert card.is_corporate is True


@pytest.mark.unit
@pytest.mark.domain
class TestPaymentResult:
    """Tests for PaymentResult entity"""

    def test_create_successful_payment_result(self):
        """Test creating a successful payment result"""
        result = PaymentResult(
            success=True,
            message="Payment successful",
            reservation_number="R123456"
        )

        assert result.success is True
        assert result.message == "Payment successful"
        assert result.reservation_number == "R123456"

    def test_create_failed_payment_result(self):
        """Test creating a failed payment result"""
        result = PaymentResult(
            success=False,
            message="Payment failed"
        )

        assert result.success is False
        assert result.message == "Payment failed"
        assert result.reservation_number is None
