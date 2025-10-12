"""Integration tests for SRTService"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from src.infrastructure.adapters.srt_service import SRTService
from src.domain.models.entities import ReservationRequest, Passenger, CreditCard, ReservationResult
from src.domain.models.enums import PassengerType, TrainType


@pytest.fixture
def srt_service():
    """Create SRTService instance for testing"""
    return SRTService()


@pytest.fixture
def sample_reservation_request():
    """Create a sample reservation request"""
    return ReservationRequest(
        departure_station="수서",
        arrival_station="부산",
        departure_date=date(2025, 1, 15),
        departure_time="100000",
        passengers=[
            Passenger(passenger_type=PassengerType.ADULT, count=2),
            Passenger(passenger_type=PassengerType.CHILD, count=1)
        ],
        train_type=TrainType.SRT
    )


class TestSRTServiceLogin:
    """Tests for SRTService login/logout"""

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_successful_login(self, mock_srt_class, srt_service):
        """Test successful login"""
        # Arrange
        mock_srt = Mock()
        mock_srt.login.return_value = True
        srt_service._srt = mock_srt

        # Act
        result = srt_service.login("test_user", "test_password")

        # Assert
        assert result is True
        assert srt_service.is_logged_in() is True
        mock_srt.login.assert_called_once_with("test_user", "test_password")

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_failed_login(self, mock_srt_class, srt_service):
        """Test failed login"""
        # Arrange
        mock_srt = Mock()
        mock_srt.login.side_effect = Exception("Login failed")
        srt_service._srt = mock_srt

        # Act
        result = srt_service.login("test_user", "wrong_password")

        # Assert
        assert result is False
        assert srt_service.is_logged_in() is False

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_logout(self, mock_srt_class, srt_service):
        """Test logout"""
        # Arrange
        mock_srt = Mock()
        srt_service._srt = mock_srt
        srt_service._logged_in = True

        # Act
        result = srt_service.logout()

        # Assert
        assert result is True
        assert srt_service.is_logged_in() is False
        mock_srt.logout.assert_called_once()


class TestSRTServiceSearchTrains:
    """Tests for SRTService search_trains"""

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_search_trains_not_logged_in(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test searching trains when not logged in"""
        # Arrange
        srt_service._logged_in = False

        # Act
        result = srt_service.search_trains(sample_reservation_request)

        # Assert
        assert result == []

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_search_trains_success(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test successful train search"""
        # Arrange
        srt_service._logged_in = True
        mock_srt = Mock()

        mock_train = Mock()
        mock_train.train_number = "S001"
        mock_train.dep_date = "20250115"
        mock_train.dep_time = "100000"
        mock_train.arr_date = "20250115"
        mock_train.arr_time = "123000"
        mock_train.adultcharge = "52000"
        mock_train.seat_count = 10

        mock_srt.search_train.return_value = [mock_train]
        srt_service._srt = mock_srt

        # Act
        result = srt_service.search_trains(sample_reservation_request)

        # Assert
        assert len(result) == 1
        assert result[0].train_number == "S001"
        assert result[0].train_type == TrainType.SRT

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_search_trains_exception(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test train search with exception"""
        # Arrange
        srt_service._logged_in = True
        mock_srt = Mock()
        mock_srt.search_train.side_effect = Exception("Search error")
        srt_service._srt = mock_srt

        # Act
        result = srt_service.search_trains(sample_reservation_request)

        # Assert
        assert result == []


class TestSRTServiceReserveTrain:
    """Tests for SRTService reserve_train"""

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_reserve_train_not_logged_in(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test reserving train when not logged in"""
        # Arrange
        srt_service._logged_in = False
        mock_schedule = Mock()

        # Act
        result = srt_service.reserve_train(mock_schedule, sample_reservation_request)

        # Assert
        assert result.success is False
        assert result.message == "Not logged in"

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_reserve_train_not_found(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test reserving train when train not found"""
        # Arrange
        srt_service._logged_in = True
        mock_srt = Mock()
        mock_srt.search_train.return_value = []
        srt_service._srt = mock_srt

        mock_schedule = Mock()
        mock_schedule.train_number = "S999"

        # Act
        result = srt_service.reserve_train(mock_schedule, sample_reservation_request)

        # Assert
        assert result.success is False
        assert result.message == "Train not found"

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_reserve_train_no_seats(self, mock_srt_class, srt_service, sample_reservation_request):
        """Test reserving train when no seats available"""
        # Arrange
        srt_service._logged_in = True
        mock_srt = Mock()

        mock_train = Mock()
        mock_train.train_number = "S001"
        mock_train.seat_available.return_value = False

        mock_srt.search_train.return_value = [mock_train]
        srt_service._srt = mock_srt

        mock_schedule = Mock()
        mock_schedule.train_number = "S001"

        # Act
        result = srt_service.reserve_train(mock_schedule, sample_reservation_request)

        # Assert
        assert result.success is False
        assert result.message == "No available seats"


class TestSRTServicePayment:
    """Tests for SRTService payment_reservation"""

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_payment_not_logged_in(self, mock_srt_class, srt_service):
        """Test payment when not logged in"""
        # Arrange
        srt_service._logged_in = False
        mock_reservation = ReservationResult(
            success=True,
            reservation_number="R123456",
            message="Success"
        )
        mock_card = CreditCard(
            number="1234567812345678",
            password="12",
            validation_number="990101",
            expire="2512",
            is_corporate=False
        )

        # Act
        result = srt_service.payment_reservation(mock_reservation, mock_card)

        # Assert
        assert result == False

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_payment_reservation_not_found(self, mock_srt_class, srt_service):
        """Test payment when reservation not found"""
        # Arrange
        srt_service._logged_in = True
        mock_srt = Mock()
        mock_srt.get_reservations.return_value = []
        srt_service._srt = mock_srt

        mock_reservation = ReservationResult(
            success=True,
            reservation_number="R123456",
            message="Success"
        )
        mock_card = CreditCard(
            number="1234567812345678",
            password="12",
            validation_number="990101",
            expire="2512",
            is_corporate=False
        )

        # Act
        result = srt_service.payment_reservation(mock_reservation, mock_card)

        # Assert
        assert result.success is False
        assert result.message == "Reservation not found"


class TestSRTServiceClear:
    """Tests for SRTService clear method"""

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_clear_session(self, mock_srt_class, srt_service):
        """Test clearing session"""
        # Arrange
        mock_srt = Mock()
        mock_srt.clear = Mock()
        srt_service._srt = mock_srt
        srt_service._logged_in = True

        # Act
        srt_service.clear()

        # Assert
        assert srt_service.is_logged_in() is False
        mock_srt.logout.assert_called_once()
        mock_srt.clear.assert_called_once()
        assert srt_service._srt is not None
        assert srt_service._srt != mock_srt  # New SRT instance created

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_clear_creates_new_instance(self, mock_srt_class, srt_service):
        """Test that clear creates a new SRT instance"""
        # Arrange
        old_srt = srt_service._srt
        old_srt.clear = Mock()
        srt_service._logged_in = True

        # Mock the SRT class to return a new instance
        new_mock_srt = Mock()
        mock_srt_class.return_value = new_mock_srt

        # Act
        srt_service.clear()

        # Assert
        mock_srt_class.assert_called_once_with(auto_login=False)
        assert srt_service._srt == new_mock_srt
