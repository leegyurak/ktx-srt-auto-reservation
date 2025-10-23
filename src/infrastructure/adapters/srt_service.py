from typing import List
from datetime import datetime
from src.domain.services.train_service import TrainService
from src.domain.models.entities import (
    Station, TrainSchedule, ReservationRequest, ReservationResult, CreditCard, PaymentResult
)
from src.domain.models.enums import TrainType
from src.infrastructure.external.srt import SRT
from src.infrastructure.mappers import PassengerMapper
from src.constants.stations import SRT_STATIONS
from src.infrastructure.external.srt import SeatType


class SRTService(TrainService):
    """SRT train service implementation"""

    def __init__(self):
        self._srt = SRT(auto_login=False)
        self._logged_in = False

    def login(self, user_id: str, password: str) -> bool:
        """Login to SRT service"""
        try:
            self._srt.login(user_id, password)
            self._logged_in = True
            return True
        except Exception as e:
            self._logged_in = False
            return False

    def logout(self) -> bool:
        """Logout from SRT service"""
        try:
            self._srt.logout()
            self._logged_in = False
            return True
        except Exception:
            return False

    def search_trains(self, request: ReservationRequest) -> list[TrainSchedule]:
        """Search for available SRT trains"""
        if not self._logged_in:
            return []

        passengers = [PassengerMapper.to_srt(p) for p in request.passengers]

        try:
            # Convert domain request to SRT format
            trains = self._srt.search_train(
                dep=request.departure_station,
                arr=request.arrival_station,
                date=request.departure_date.strftime("%Y%m%d"),
                time=request.departure_time,
                passengers=passengers,
                available_only=False,
            )

            schedules: list[TrainSchedule] = []
            for train in trains:
                schedule = TrainSchedule(
                    train_number=train.train_number,
                    departure_station=request.departure_station,
                    arrival_station=request.arrival_station,
                    departure_time=self._parse_time(train.dep_date + train.dep_time),
                    arrival_time=self._parse_time(train.arr_date + train.arr_time),
                    train_type=TrainType.SRT,
                    available_seats=self._get_available_seats(train),
                    price=getattr(train, 'adultcharge', None)
                )
                schedules.append(schedule)

            return schedules
        except Exception:
            return []

    def reserve_train(self, schedules: list[TrainSchedule], request: ReservationRequest) -> ReservationResult:
        """Reserve an SRT train"""
        if not self._logged_in:
            return ReservationResult(success=False, message="Not logged in")

        try:
            # Convert passengers to SRT format
            passengers = [PassengerMapper.to_srt(p) for p in request.passengers]

            # Find the trains for reservation
            trains = self._srt.search_train(
                dep=request.departure_station,
                arr=request.arrival_station,
                date=request.departure_date.strftime("%Y%m%d"),
                time=request.departure_time,
                passengers=passengers,
                available_only=False,
            )

            schedules.sort(key=lambda x: x.departure_time)
            target_train_numbers = [schedule.train_number for schedule in schedules]

            for train in trains:
                if train.train_number in target_train_numbers and train.seat_available():
                    # Check for special seat preference
                    if train.special_seat_available() and request.is_special_seat_allowed:
                        reservation = self._srt.reserve(train=train, passengers=passengers, option=SeatType.SPECIAL_ONLY)
                    else:
                        reservation = self._srt.reserve(train=train, passengers=passengers, option=SeatType.GENERAL_ONLY)

                    if reservation:
                        return ReservationResult(
                            success=True,
                            reservation_number=reservation.reservation_number,
                            message="Reservation successful",
                            train_schedule=[
                                schedule
                                for schedule in schedules
                                if train.train_number == schedule.train_number
                            ][0],
                        )
                    else:
                        continue

            return ReservationResult(success=False, message="Any requested trains have no seats")

        except Exception as e:
            return ReservationResult(success=False, message=f"Reservation error: {e}")

    def payment_reservation(self, reservation: ReservationResult, credit_card: CreditCard) -> PaymentResult:
        """Pay for a reservation with credit card"""
        if not self._logged_in:
            return PaymentResult(success=False, message="Not logged in")

        srt_reservations = self._srt.get_reservations(paid_only=False)
        target_reservation = None

        for srt_reservation in srt_reservations:
            if srt_reservation.reservation_number == reservation.reservation_number:
                target_reservation = srt_reservation
                break

        if not target_reservation:
            return PaymentResult(success=False, message="Reservation not found")
        
        is_success = self._srt.pay_with_card(
            target_reservation,
            number=credit_card.number,
            password=credit_card.password,
            validation_number=credit_card.validation_number,
            expire_date=credit_card.expire,
            card_type="J" if not credit_card.is_corporate else "S",
        )

        if is_success:
            return PaymentResult(success=True, message="Payment successful", reservation_number=target_reservation.reservation_number)
        else:
            return PaymentResult(success=False, message="Payment failed")

    def get_stations(self) -> List[Station]:
        """Get list of SRT stations"""
        return [Station(station.name, station.code) for station in SRT_STATIONS]

    def is_logged_in(self) -> bool:
        """Check if logged in to SRT service"""
        return self._logged_in

    @property
    def service_name(self) -> str:
        """Name of the service"""
        return "SRT"

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime"""
        return datetime.strptime(time_str, "%Y%m%d%H%M%S")

    def _get_available_seats(self, train) -> int:
        """Get available seats count"""
        try:
            # Try to get seat availability information
            return getattr(train, 'seat_count', 0)
        except:
            return 0
        
    def clear(self) -> None:
        self.logout()
        self._srt.clear()
        self._srt = SRT(auto_login=False)
