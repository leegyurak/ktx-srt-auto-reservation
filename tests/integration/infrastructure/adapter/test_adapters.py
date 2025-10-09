"""Integration tests for service adapters with comprehensive coverage"""
import pytest
from unittest.mock import Mock, patch
from src.infrastructure.adapters.ktx_service import KTXService
from src.infrastructure.adapters.srt_service import SRTService


@pytest.mark.integration
@pytest.mark.service
class TestKTXServiceIntegration:
    """Comprehensive integration tests for KTXService"""

    @pytest.fixture
    def ktx_service(self):
        """Create KTXService instance"""
        return KTXService()

    def test_service_initialization(self, ktx_service):
        """Test that KTXService initializes correctly"""
        assert ktx_service is not None
        assert ktx_service.service_name == "KTX"
        assert ktx_service.is_logged_in() is False

    def test_service_implements_train_service(self, ktx_service):
        """Test that KTXService properly implements TrainService interface"""
        from src.domain.services.train_service import TrainService
        assert isinstance(ktx_service, TrainService)

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_login_flow(self, mock_korail_class, ktx_service):
        """Test complete login flow"""
        mock_korail = Mock()
        mock_korail.login.return_value = True
        ktx_service._korail = mock_korail

        # Login
        result = ktx_service.login("user", "pass")
        assert result is True
        assert ktx_service.is_logged_in() is True

        # Logout
        result = ktx_service.logout()
        assert result is True
        assert ktx_service.is_logged_in() is False

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_search_trains_with_passengers(
        self, mock_korail_class, ktx_service, sample_reservation_request, mock_korail_train
    ):
        """Test train search with multiple passenger types"""
        ktx_service._logged_in = True
        mock_korail = Mock()
        mock_korail.search_train.return_value = [mock_korail_train]
        ktx_service._korail = mock_korail

        trains = ktx_service.search_trains(sample_reservation_request)

        assert len(trains) == 1
        assert trains[0].train_number == "001"
        mock_korail.search_train.assert_called_once()

    @patch('src.infrastructure.adapters.ktx_service.Korail')
    def test_reserve_train_with_payment(
        self, mock_korail_class, ktx_service, sample_train_schedule,
        sample_reservation_request, personal_credit_card, mock_korail_train, mock_korail_reservation
    ):
        """Test complete reservation and payment flow"""
        ktx_service._logged_in = True
        mock_korail = Mock()

        # Setup mocks
        mock_korail_train.has_seat.return_value = True
        mock_korail.search_train.return_value = [mock_korail_train]
        mock_korail.reserve.return_value = mock_korail_reservation
        mock_korail.reservations.return_value = mock_korail_reservation
        mock_korail.pay_with_card.return_value = True

        ktx_service._korail = mock_korail

        # Reserve
        result = ktx_service.reserve_train(sample_train_schedule, sample_reservation_request)
        assert result.success is True
        assert result.reservation_number == "R123456"

        # Payment
        payment_result = ktx_service.payment_reservation(result, personal_credit_card)
        assert payment_result.success is True


@pytest.mark.integration
@pytest.mark.service
class TestSRTServiceIntegration:
    """Comprehensive integration tests for SRTService"""

    @pytest.fixture
    def srt_service(self):
        """Create SRTService instance"""
        return SRTService()

    def test_service_initialization(self, srt_service):
        """Test that SRTService initializes correctly"""
        assert srt_service is not None
        assert srt_service.service_name == "SRT"
        assert srt_service.is_logged_in() is False

    def test_service_implements_train_service(self, srt_service):
        """Test that SRTService properly implements TrainService interface"""
        from src.domain.services.train_service import TrainService
        assert isinstance(srt_service, TrainService)

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_login_flow(self, mock_srt_class, srt_service):
        """Test complete login flow"""
        mock_srt = Mock()
        mock_srt.login.return_value = True
        srt_service._srt = mock_srt

        # Login
        result = srt_service.login("user", "pass")
        assert result is True
        assert srt_service.is_logged_in() is True

        # Logout
        result = srt_service.logout()
        assert result is True
        assert srt_service.is_logged_in() is False

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_search_trains_with_passengers(
        self, mock_srt_class, srt_service, sample_srt_reservation_request, mock_srt_train
    ):
        """Test train search with passengers"""
        srt_service._logged_in = True
        mock_srt = Mock()
        mock_srt.search_train.return_value = [mock_srt_train]
        srt_service._srt = mock_srt

        trains = srt_service.search_trains(sample_srt_reservation_request)

        assert len(trains) == 1
        assert trains[0].train_number == "S001"
        mock_srt.search_train.assert_called_once()

    @patch('src.infrastructure.adapters.srt_service.SRT')
    def test_reserve_train_with_payment(
        self, mock_srt_class, srt_service, sample_srt_train_schedule,
        sample_srt_reservation_request, corporate_credit_card, mock_srt_train, mock_srt_reservation
    ):
        """Test complete reservation and payment flow with corporate card"""
        srt_service._logged_in = True
        mock_srt = Mock()

        # Setup mocks
        mock_srt_train.seat_available.return_value = True
        mock_srt.search_train.return_value = [mock_srt_train]
        mock_srt.reserve.return_value = mock_srt_reservation
        mock_srt.get_reservations.return_value = [mock_srt_reservation]
        mock_srt.pay_with_card.return_value = True

        srt_service._srt = mock_srt

        # Reserve
        result = srt_service.reserve_train(sample_srt_train_schedule, sample_srt_reservation_request)
        assert result.success is True
        assert result.reservation_number == "R123456"

        # Payment with corporate card
        payment_result = srt_service.payment_reservation(result, corporate_credit_card)
        assert payment_result.success is True


@pytest.mark.integration
@pytest.mark.service
@pytest.mark.slow
class TestCrossServiceComparison:
    """Tests comparing KTX and SRT service behaviors"""

    def test_both_services_implement_same_interface(self):
        """Test that both services implement TrainService interface"""
        from src.domain.services.train_service import TrainService

        ktx = KTXService()
        srt = SRTService()

        assert isinstance(ktx, TrainService)
        assert isinstance(srt, TrainService)

    def test_both_services_have_consistent_behavior(self):
        """Test that both services behave consistently"""
        ktx = KTXService()
        srt = SRTService()

        # Both should start logged out
        assert ktx.is_logged_in() is False
        assert srt.is_logged_in() is False

        # Both should have service names
        assert ktx.service_name == "KTX"
        assert srt.service_name == "SRT"
