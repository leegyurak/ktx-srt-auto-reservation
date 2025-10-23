from abc import ABC, abstractmethod
from typing import List

from src.domain.models.entities import (
    Station, TrainSchedule, ReservationRequest, ReservationResult
)


class TrainService(ABC):
    """Abstract base class for train reservation services"""

    @abstractmethod
    def login(self, user_id: str, password: str) -> bool:
        """Login to the train service"""
        pass

    @abstractmethod
    def logout(self) -> bool:
        """Logout from the train service"""
        pass

    @abstractmethod
    def search_trains(self, request: ReservationRequest) -> List[TrainSchedule]:
        """Search for available trains"""
        pass

    @abstractmethod
    def reserve_train(self, schedule: list[TrainSchedule], request: ReservationRequest) -> ReservationResult:
        """Reserve a specific train"""
        pass

    @abstractmethod
    def get_stations(self) -> List[Station]:
        """Get list of available stations"""
        pass

    @abstractmethod
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear client sessions"""
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Name of the train service (KTX, SRT, etc.)"""
        pass