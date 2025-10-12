"""Integration tests for KTXService"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from src.infrastructure.adapters.ktx_service import KTXService
from src.domain.models.entities import ReservationRequest, Passenger, CreditCard, ReservationResult
from src.domain.models.enums import PassengerType, TrainType


@pytest.fixture
def ktx_service():
    """Create KTXService instance for testing"""
    return KTXService()


@pytest.fixture
def sample_reservation_request():
    """Create a sample reservation request"""
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


class TestKTXServiceLogin:
    """Tests for KTXService login/logout"""

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_successful_login(self, mock_korail_class, ktx_service):
        """Test successful login"""
        # Arrange
        mock_korail = Mock()
        mock_korail.login.return_value = True
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.login("test_user", "test_password")

        # Assert
        assert result is True
        assert ktx_service.is_logged_in() is True
        mock_korail.login.assert_called_once_with("test_user", "test_password")

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_failed_login(self, mock_korail_class, ktx_service):
        """Test failed login"""
        # Arrange
        mock_korail = Mock()
        mock_korail.login.return_value = False
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.login("test_user", "wrong_password")

        # Assert
        assert result is False
        assert ktx_service.is_logged_in() is False

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_login_exception(self, mock_korail_class, ktx_service):
        """Test login with exception"""
        # Arrange
        mock_korail = Mock()
        mock_korail.login.side_effect = Exception("Network error")
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.login("test_user", "test_password")

        # Assert
        assert result is False
        assert ktx_service.is_logged_in() is False

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_logout(self, mock_korail_class, ktx_service):
        """Test logout"""
        # Arrange
        mock_korail = Mock()
        ktx_service._korail = mock_korail
        ktx_service._logged_in = True

        # Act
        result = ktx_service.logout()

        # Assert
        assert result is True
        assert ktx_service.is_logged_in() is False
        mock_korail.logout.assert_called_once()


class TestKTXServiceSearchTrains:
    """Tests for KTXService search_trains"""

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_search_trains_not_logged_in(self, mock_korail_class, ktx_service, sample_reservation_request):
        """Test searching trains when not logged in"""
        # Arrange
        ktx_service._logged_in = False

        # Act
        result = ktx_service.search_trains(sample_reservation_request)

        # Assert
        assert result == []

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_search_trains_success(self, mock_korail_class, ktx_service, sample_reservation_request):
        """Test successful train search"""
        # Arrange
        ktx_service._logged_in = True
        mock_korail = Mock()

        mock_train = Mock()
        mock_train.train_no = "001"
        mock_train.dep_date = "20250115"
        mock_train.dep_time = "100000"
        mock_train.arr_date = "20250115"
        mock_train.arr_time = "123000"
        mock_train.train_type = "KTX"
        mock_train.adultcharge = "59800"
        mock_train.seat_count = 10

        mock_korail.search_train.return_value = [mock_train]
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.search_trains(sample_reservation_request)

        # Assert
        assert len(result) == 1
        assert result[0].train_number == "001"
        assert result[0].train_type == TrainType.KTX

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_search_trains_exception(self, mock_korail_class, ktx_service, sample_reservation_request):
        """Test train search with exception"""
        # Arrange
        ktx_service._logged_in = True
        mock_korail = Mock()
        mock_korail.search_train.side_effect = Exception("Search error")
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.search_trains(sample_reservation_request)

        # Assert
        assert result == []


class TestKTXServiceReserveTrain:
    """Tests for KTXService reserve_train"""

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_not_logged_in(self, mock_korail_class, ktx_service, sample_reservation_request, sample_train_schedule):
        """Test reserving train when not logged in"""
        # Arrange
        ktx_service._logged_in = False
        mock_schedules = [sample_train_schedule]

        # Act
        result = ktx_service.reserve_train(mock_schedules, sample_reservation_request)

        # Assert
        assert result.success is False
        assert result.message == "Not logged in"

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_not_found(self, mock_korail_class, ktx_service, sample_reservation_request, sample_train_schedule):
        """Test reserving train when train not found"""
        # Arrange
        ktx_service._logged_in = True
        mock_korail = Mock()
        mock_korail.search_train.return_value = []
        ktx_service._korail = mock_korail

        mock_schedules = [sample_train_schedule]

        # Act
        result = ktx_service.reserve_train(mock_schedules, sample_reservation_request)

        # Assert
        assert result.success is False
        assert result.message == "Any requested trains have no seats"

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_success_first_train(self, mock_korail_class, ktx_service, sample_reservation_request, sample_train_schedule):
        """Test successful reservation with first train"""
        # Arrange
        ktx_service._logged_in = True
        mock_korail = Mock()

        mock_train = Mock()
        mock_train.train_no = "001"
        mock_train.has_seat.return_value = True

        mock_reservation = Mock()
        mock_reservation.rsv_id = "R123456"

        mock_korail.search_train.return_value = [mock_train]
        mock_korail.reserve.return_value = mock_reservation
        ktx_service._korail = mock_korail

        mock_schedules = [sample_train_schedule]

        # Act
        result = ktx_service.reserve_train(mock_schedules, sample_reservation_request)

        # Assert
        assert result.success is True
        assert result.reservation_number == "R123456"
        assert result.train_schedule == sample_train_schedule

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_success_second_train(self, mock_korail_class, ktx_service, sample_reservation_request):
        """Test successful reservation with second train when first has no seats"""
        # Arrange
        from src.domain.models.entities import TrainSchedule

        ktx_service._logged_in = True
        mock_korail = Mock()

        # Create two schedules
        schedule1 = TrainSchedule(
            train_number="001",
            departure_station="서울",
            arrival_station="부산",
            departure_time=datetime(2025, 1, 15, 10, 0, 0),
            arrival_time=datetime(2025, 1, 15, 12, 30, 0),
            train_type=TrainType.KTX,
            available_seats=0,
            price="59800"
        )
        schedule2 = TrainSchedule(
            train_number="002",
            departure_station="서울",
            arrival_station="부산",
            departure_time=datetime(2025, 1, 15, 11, 0, 0),
            arrival_time=datetime(2025, 1, 15, 13, 30, 0),
            train_type=TrainType.KTX,
            available_seats=10,
            price="59800"
        )

        # Mock trains
        mock_train1 = Mock()
        mock_train1.train_no = "001"
        mock_train1.has_seat.return_value = False

        mock_train2 = Mock()
        mock_train2.train_no = "002"
        mock_train2.has_seat.return_value = True

        mock_reservation = Mock()
        mock_reservation.rsv_id = "R123456"

        mock_korail.search_train.return_value = [mock_train1, mock_train2]
        mock_korail.reserve.return_value = mock_reservation
        ktx_service._korail = mock_korail

        mock_schedules = [schedule1, schedule2]

        # Act
        result = ktx_service.reserve_train(mock_schedules, sample_reservation_request)

        # Assert
        assert result.success is True
        assert result.reservation_number == "R123456"
        assert result.train_schedule.train_number == "002"

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_multiple_schedules(self, mock_korail_class, ktx_service, sample_reservation_request):
        """Test reservation with multiple schedules"""
        # Arrange
        from src.domain.models.entities import TrainSchedule

        ktx_service._logged_in = True
        mock_korail = Mock()

        # Create three schedules
        schedules = [
            TrainSchedule(
                train_number=f"00{i}",
                departure_station="서울",
                arrival_station="부산",
                departure_time=datetime(2025, 1, 15, 10 + i, 0, 0),
                arrival_time=datetime(2025, 1, 15, 12 + i, 30, 0),
                train_type=TrainType.KTX,
                available_seats=10,
                price="59800"
            )
            for i in range(1, 4)
        ]

        # Mock trains - only third one has seats
        mock_trains = []
        for i in range(1, 4):
            mock_train = Mock()
            mock_train.train_no = f"00{i}"
            mock_train.has_seat.return_value = (i == 3)
            mock_trains.append(mock_train)

        mock_reservation = Mock()
        mock_reservation.rsv_id = "R123456"

        mock_korail.search_train.return_value = mock_trains
        mock_korail.reserve.return_value = mock_reservation
        ktx_service._korail = mock_korail

        # Act
        result = ktx_service.reserve_train(schedules, sample_reservation_request)

        # Assert
        assert result.success is True
        assert result.reservation_number == "R123456"
        assert result.train_schedule.train_number == "003"


class TestKTXServicePayment:
    """Tests for KTXService payment_reservation"""

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_payment_not_logged_in(self, mock_korail_class, ktx_service):
        """Test payment when not logged in"""
        # Arrange
        ktx_service._logged_in = False
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
        result = ktx_service.payment_reservation(mock_reservation, mock_card)

        # Assert
        assert result.success is False
        assert result.message == "Not logged in"

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_payment_reservation_not_found(self, mock_korail_class, ktx_service):
        """Test payment when reservation not found"""
        # Arrange
        ktx_service._logged_in = True
        mock_korail = Mock()
        mock_korail.reservations.return_value = None
        ktx_service._korail = mock_korail

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
        result = ktx_service.payment_reservation(mock_reservation, mock_card)

        # Assert
        assert result.success is False
        assert result.message == "Reservation not found"


class TestKTXServiceClear:
    """Tests for KTXService clear method"""

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_clear_session(self, mock_korail_class, ktx_service):
        """Test clearing session"""
        # Arrange
        mock_korail = Mock()
        ktx_service._korail = mock_korail
        ktx_service._logged_in = True

        # Act
        ktx_service.clear()

        # Assert
        assert ktx_service.is_logged_in() is False
        mock_korail.logout.assert_called_once()
        assert ktx_service._korail is not None
        assert ktx_service._korail != mock_korail  # New Korail instance created

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_clear_creates_new_instance(self, mock_korail_class, ktx_service):
        """Test that clear creates a new Korail instance"""
        # Arrange
        old_korail = ktx_service._korail
        ktx_service._logged_in = True

        # Mock the Korail class to return a new instance
        new_mock_korail = Mock()
        mock_korail_class.return_value = new_mock_korail

        # Act
        ktx_service.clear()

        # Assert
        mock_korail_class.assert_called_once_with(auto_login=False)
        assert ktx_service._korail == new_mock_korail
