from typing import List
from datetime import datetime
from src.domain.services.train_service import TrainService
from src.domain.models.entities import (
    Station, TrainSchedule, ReservationRequest, ReservationResult, CreditCard, PaymentResult
)
from src.domain.models.enums import TrainType
from src.infrastructure.external.ktx import Korail, TrainType as KorailTrainType
from src.infrastructure.mappers import PassengerMapper
from src.constants.stations import KTX_STATIONS
from src.infrastructure.external.ktx import ReserveOption

class KTXService(TrainService):
    """KTX/Korail train service implementation"""

    def __init__(self):
        self._korail = Korail(auto_login=False)
        self._logged_in = False

    def login(self, user_id: str, password: str) -> bool:
        """Login to Korail service"""
        try:
            result = self._korail.login(user_id, password)
            self._logged_in = result
            return result
        except Exception as e:
            self._logged_in = False
            return False

    def logout(self) -> bool:
        """Logout from Korail service"""
        try:
            self._korail.logout()
            self._logged_in = False
            return True
        except Exception:
            return False

    def search_trains(self, request: ReservationRequest) -> List[TrainSchedule]:
        """Search for available KTX trains"""
        if not self._logged_in:
            return []

        try:
            # Convert domain request to Korail format
            trains = self._korail.search_train(
                dep=request.departure_station,
                arr=request.arrival_station,
                date=request.departure_date.strftime("%Y%m%d"),
                time=request.departure_time,
                train_type=KorailTrainType.KTX,
                include_no_seats=True,
            )

            schedules = []
            for train in trains:
                schedule = TrainSchedule(
                    train_number=getattr(train, 'train_no', ''),
                    departure_station=request.departure_station,
                    arrival_station=request.arrival_station,
                    departure_time=self._parse_time(train.dep_date + train.dep_time),
                    arrival_time=self._parse_time(train.arr_date + train.arr_time),
                    train_type=self._convert_train_type(getattr(train, 'train_type', '')),
                    available_seats=self._get_available_seats(train),
                    price=getattr(train, 'adultcharge', None)
                )
                schedules.append(schedule)

            return schedules
        except Exception:
            return []

    def reserve_train(self, schedules: list[TrainSchedule], request: ReservationRequest) -> ReservationResult:
        """Reserve a KTX train"""
        if not self._logged_in:
            return ReservationResult(success=False, message="Not logged in")

        try:
            # Convert passengers to Korail format
            passengers = [PassengerMapper.to_korail(p) for p in request.passengers]

            # Find the train again for reservation
            trains = self._korail.search_train(
                dep=request.departure_station,
                arr=request.arrival_station,
                date=request.departure_date.strftime("%Y%m%d"),
                time=request.departure_time,
                passengers=passengers,
                train_type=KorailTrainType.KTX,
                include_no_seats=True,
            )

            schedules.sort(key=lambda x: x.departure_time)
            target_train_numbers = [schedule.train_number for schedule in schedules]

            for train in trains:
                if train.train_no in target_train_numbers and train.has_seat():
                    # Check for special seat preference
                    if train.has_special_seat() and request.is_special_seat_allowed:
                        reservation = self._korail.reserve(train=train, passengers=passengers, option=ReserveOption.SPECIAL_ONLY)
                    else:
                        reservation = self._korail.reserve(train=train, passengers=passengers, option=ReserveOption.GENERAL_ONLY)

                    if reservation:
                        return ReservationResult(
                            success=True,
                            reservation_number=reservation.rsv_id,
                            message="Reservation successful",
                            train_schedule=[
                                schedule
                                for schedule in schedules
                                if train.train_no == schedule.train_number
                            ][0],
                        )
                    else:
                        continue

            return ReservationResult(success=False, message="Any requested trains have no seats")

        except Exception as e:
            return ReservationResult(success=False, message=f"Reservation error: {e}")

    def get_stations(self) -> List[Station]:
        """Get list of KTX stations"""
        return [Station(station.name, station.code) for station in KTX_STATIONS]

    def is_logged_in(self) -> bool:
        """Check if logged in to KTX service"""
        return self._logged_in

    @property
    def service_name(self) -> str:
        """Name of the service"""
        return "KTX"

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime"""
        return datetime.strptime(time_str, "%Y%m%d%H%M%S")

    def _convert_train_type(self, train_type_str: str) -> TrainType:
        """Convert Korail train type to domain train type"""
        if "KTX" in train_type_str.upper():
            return TrainType.KTX
        elif "무궁화" in train_type_str:
            return TrainType.MUGUNGHWA
        elif "새마을" in train_type_str:
            return TrainType.SAEMAEUL
        else:
            return TrainType.KTX

    def _get_available_seats(self, train) -> int:
        """Get available seats count"""
        try:
            # Try to get seat availability information
            return getattr(train, 'seat_count', 0)
        except:
            return 0

    def payment_reservation(self, reservation: ReservationResult, credit_card: CreditCard) -> PaymentResult:
        """Pay for a reservation with credit card"""
        if not self._logged_in:
            return PaymentResult(success=False, message="Not logged in")

        target_reservation = self._korail.reservations(reservation.reservation_number)

        if not target_reservation:
            return PaymentResult(success=False, message="Reservation not found")

        is_success = self._korail.pay_with_card(
            target_reservation,
            card_number=credit_card.number,
            card_password=credit_card.password,
            birthday=credit_card.validation_number,
            card_expire=credit_card.expire,
            card_type="J" if not credit_card.is_corporate else "S",
        )

        if is_success:
            return PaymentResult(success=True, message="Payment successful", reservation_number=target_reservation.rsv_id)
        else:
            return PaymentResult(success=False, message="Payment failed")
        
    def clear(self) -> None:
        self.logout()
        self._korail = Korail(auto_login=False)
