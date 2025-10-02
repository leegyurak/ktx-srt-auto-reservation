"""Domain entities and value objects"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date

from src.domain.models.enums import PassengerType, TrainType


@dataclass
class Passenger:
    """승객 정보"""
    passenger_type: PassengerType
    count: int = 1


@dataclass
class Station:
    """역 정보"""
    name: str
    code: str


@dataclass
class TrainSchedule:
    """열차 스케줄 정보"""
    train_number: str
    departure_station: str
    arrival_station: str
    departure_time: datetime
    arrival_time: datetime
    train_type: TrainType
    available_seats: int
    price: Optional[int] = None


@dataclass
class ReservationRequest:
    """예약 요청 정보"""
    departure_station: str
    arrival_station: str
    departure_date: date
    departure_time: Optional[str] = None
    passengers: List[Passenger] = None
    train_type: Optional[TrainType] = None

    def __post_init__(self):
        if self.passengers is None:
            self.passengers = [Passenger(PassengerType.ADULT, 1)]


@dataclass
class ReservationResult:
    """예약 결과"""
    success: bool
    reservation_number: Optional[str] = None
    message: str = ""
    train_schedule: Optional[TrainSchedule] = None


@dataclass
class CreditCard:
    """신용카드 정보"""
    number: str
    password: str
    validation_number: str
    expire: str
    is_corporate: bool


@dataclass
class PaymentResult:
    """결제 결과"""
    success: bool
    message: str
    reservation_number: Optional[str] = None