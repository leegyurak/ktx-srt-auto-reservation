"""Unit tests for TrainService abstract base class"""
import pytest
from abc import ABC
from src.domain.services.train_service import TrainService
from src.domain.models.entities import Station, TrainSchedule, ReservationRequest, ReservationResult
from datetime import datetime, date


@pytest.mark.unit
@pytest.mark.domain
class TestTrainServiceInterface:
    """Tests for TrainService abstract interface"""

    def test_train_service_is_abstract(self):
        """Test that TrainService is an abstract base class"""
        assert issubclass(TrainService, ABC)

    def test_cannot_instantiate_train_service(self):
        """Test that TrainService cannot be instantiated directly"""
        with pytest.raises(TypeError):
            TrainService()

    def test_train_service_has_required_methods(self):
        """Test that TrainService defines all required abstract methods"""
        required_methods = [
            'login',
            'logout',
            'search_trains',
            'reserve_train',
            'get_stations',
            'is_logged_in',
        ]

        for method_name in required_methods:
            assert hasattr(TrainService, method_name)
            method = getattr(TrainService, method_name)
            assert callable(method)

    def test_train_service_has_service_name_property(self):
        """Test that TrainService defines service_name property"""
        assert hasattr(TrainService, 'service_name')


@pytest.mark.unit
@pytest.mark.domain
class TestTrainServiceImplementation:
    """Tests for implementing TrainService"""

    def test_concrete_implementation_can_be_created(self):
        """Test that a concrete implementation of TrainService can be created"""

        class ConcreteTrainService(TrainService):
            def login(self, user_id: str, password: str) -> bool:
                return True

            def logout(self) -> bool:
                return True

            def search_trains(self, request: ReservationRequest) -> list[TrainSchedule]:
                return []

            def reserve_train(self, schedule: TrainSchedule, request: ReservationRequest) -> ReservationResult:
                return ReservationResult(success=True, message="Test")

            def get_stations(self) -> list[Station]:
                return []

            def is_logged_in(self) -> bool:
                return True

            @property
            def service_name(self) -> str:
                return "Test Service"

        # Should not raise any errors
        service = ConcreteTrainService()
        assert service is not None
        assert isinstance(service, TrainService)

    def test_incomplete_implementation_cannot_be_instantiated(self):
        """Test that incomplete implementations cannot be instantiated"""

        class IncompleteService(TrainService):
            def login(self, user_id: str, password: str) -> bool:
                return True
            # Missing other required methods

        with pytest.raises(TypeError):
            IncompleteService()

    def test_concrete_implementation_methods_work(self):
        """Test that methods in concrete implementation work correctly"""

        class TestService(TrainService):
            def __init__(self):
                self._logged_in = False

            def login(self, user_id: str, password: str) -> bool:
                self._logged_in = True
                return True

            def logout(self) -> bool:
                self._logged_in = False
                return True

            def search_trains(self, request: ReservationRequest) -> list[TrainSchedule]:
                return [
                    TrainSchedule(
                        train_number="001",
                        departure_station="서울",
                        arrival_station="부산",
                        departure_time=datetime(2025, 1, 15, 10, 0),
                        arrival_time=datetime(2025, 1, 15, 12, 30),
                        train_type=request.train_type,
                        available_seats=10,
                        price=59800
                    )
                ]

            def reserve_train(self, schedule: TrainSchedule, request: ReservationRequest) -> ReservationResult:
                return ReservationResult(
                    success=True,
                    reservation_number="R123",
                    message="Success"
                )

            def get_stations(self) -> list[Station]:
                return [Station("서울", "0001"), Station("부산", "0002")]

            def is_logged_in(self) -> bool:
                return self._logged_in

            @property
            def service_name(self) -> str:
                return "Test Train Service"

        service = TestService()

        # Test login
        assert service.login("user", "pass") is True
        assert service.is_logged_in() is True

        # Test service name
        assert service.service_name == "Test Train Service"

        # Test get stations
        stations = service.get_stations()
        assert len(stations) == 2
        assert stations[0].name == "서울"

        # Test logout
        assert service.logout() is True
        assert service.is_logged_in() is False
