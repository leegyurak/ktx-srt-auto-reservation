"""Passenger mapper for converting between domain and infrastructure models"""
from src.domain.models.entities import Passenger
from src.domain.models.enums import PassengerType
from src.infrastructure.external.ktx import AdultPassenger, ChildPassenger, SeniorPassenger, Passenger as KorailPessenger
from src.infrastructure.external.srt import Adult, Child, Senior, Passenger as SRTPessenger


class PassengerMapper:
    """Maps a single passenger between domain and infrastructure layers"""

    @staticmethod
    def to_korail(passenger: Passenger) -> KorailPessenger:
        """Convert a single domain passenger to Korail format"""
        match passenger.passenger_type:
            case PassengerType.ADULT:
                return AdultPassenger(count=passenger.count)
            case PassengerType.CHILD:
                return ChildPassenger(count=passenger.count)
            case PassengerType.SENIOR:
                return SeniorPassenger(count=passenger.count)

    @staticmethod
    def to_srt(passenger: Passenger) -> SRTPessenger:
        """Convert a single domain passenger to SRT format"""
        match passenger.passenger_type:
            case PassengerType.ADULT:
                return Adult(count=passenger.count)
            case PassengerType.CHILD:
                return Child(count=passenger.count)
            case PassengerType.SENIOR:
                return Senior(count=passenger.count)
