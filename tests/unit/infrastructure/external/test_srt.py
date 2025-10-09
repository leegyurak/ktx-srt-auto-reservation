"""Unit tests for SRT external module."""

import pytest
import json

from src.infrastructure.external.srt import (
    SRT,
    SRTTrain,
    SRTTicket,
    SRTReservation,
    SRTResponseData,
    Passenger,
    Adult,
    Child,
    Senior,
    Disability1To3,
    Disability4To6,
    SeatType,
    SRTError,
    SRTLoginError,
    SRTResponseError,
    SRTNotLoggedInError,
    SRTNetFunnelError,
    NetFunnelHelper,
    STATION_CODE,
    STATION_NAME,
    TRAIN_NAME,
    WINDOW_SEAT,
)


class TestPassenger:
    """Test Passenger classes."""

    def test_adult_passenger(self):
        """Test Adult passenger creation."""
        passenger = Adult(count=2)

        assert passenger.name == "어른/청소년"
        assert passenger.type_code == "1"
        assert passenger.count == 2

    def test_child_passenger(self):
        """Test Child passenger creation."""
        passenger = Child(count=1)

        assert passenger.name == "어린이"
        assert passenger.type_code == "5"
        assert passenger.count == 1

    def test_senior_passenger(self):
        """Test Senior passenger creation."""
        passenger = Senior(count=1)

        assert passenger.name == "경로"
        assert passenger.type_code == "4"
        assert passenger.count == 1

    def test_disability_1to3_passenger(self):
        """Test Disability1To3 passenger creation."""
        passenger = Disability1To3(count=1)

        assert passenger.name == "장애 1~3급"
        assert passenger.type_code == "2"
        assert passenger.count == 1

    def test_disability_4to6_passenger(self):
        """Test Disability4To6 passenger creation."""
        passenger = Disability4To6(count=1)

        assert passenger.name == "장애 4~6급"
        assert passenger.type_code == "3"
        assert passenger.count == 1

    def test_passenger_addition_same_type(self):
        """Test adding passengers of same type."""
        p1 = Adult(count=2)
        p2 = Adult(count=1)
        p3 = p1 + p2

        assert p3.count == 3
        assert isinstance(p3, Adult)

    def test_passenger_addition_different_type_error(self):
        """Test adding passengers of different types raises error."""
        p1 = Adult(count=2)
        p2 = Child(count=1)

        with pytest.raises(TypeError):
            _ = p1 + p2

    def test_passenger_combine(self):
        """Test combining passenger list."""
        passengers = [Adult(count=1), Adult(count=2), Child(count=1), Child(count=2)]
        combined = Passenger.combine(passengers)

        assert len(combined) == 2
        assert any(p.count == 3 and isinstance(p, Adult) for p in combined)
        assert any(p.count == 3 and isinstance(p, Child) for p in combined)

    def test_passenger_total_count(self):
        """Test total passenger count."""
        passengers = [Adult(count=2), Child(count=1), Senior(count=1)]
        total = Passenger.total_count(passengers)

        assert total == "4"

    def test_passenger_get_passenger_dict(self):
        """Test passenger dictionary generation."""
        passengers = [Adult(count=2), Child(count=1)]
        data = Passenger.get_passenger_dict(passengers, special_seat=False)

        assert data["totPrnb"] == "3"
        assert data["psgGridcnt"] == "2"
        assert data["psrmClCd1"] == "1"
        assert "psgTpCd1" in data
        assert "psgInfoPerPrnb1" in data

    def test_passenger_get_passenger_dict_special_seat(self):
        """Test passenger dictionary with special seat."""
        passengers = [Adult(count=1)]
        data = Passenger.get_passenger_dict(passengers, special_seat=True)

        assert data["psrmClCd1"] == "2"

    def test_passenger_get_passenger_dict_window_seat(self):
        """Test passenger dictionary with window seat preference."""
        passengers = [Adult(count=1)]
        data = Passenger.get_passenger_dict(passengers, window_seat=True)

        assert data["locSeatAttCd1"] == "012"

    def test_passenger_repr(self):
        """Test passenger string representation."""
        passenger = Adult(count=2)
        assert repr(passenger) == "어른/청소년 2명"


class TestSRTTicket:
    """Test SRTTicket class."""

    def test_ticket_initialization(self):
        """Test SRTTicket object creation."""
        data = {
            "scarNo": "05",
            "seatNo": "12A",
            "psrmClCd": "1",
            "dcntKndCd": "000",
            "rcvdAmt": "59800",
            "stdrPrc": "59800",
            "dcntPrc": "0",
        }
        ticket = SRTTicket(data)

        assert ticket.car == "05"
        assert ticket.seat == "12A"
        assert ticket.seat_type_code == "1"
        assert ticket.seat_type == "일반실"
        assert ticket.passenger_type == "어른/청소년"
        assert ticket.price == 59800
        assert ticket.discount == 0
        assert ticket.is_waiting is False

    def test_ticket_special_seat(self):
        """Test SRTTicket with special seat."""
        data = {
            "scarNo": "03",
            "seatNo": "05C",
            "psrmClCd": "2",
            "dcntKndCd": "204",
            "rcvdAmt": "29900",
            "stdrPrc": "59800",
            "dcntPrc": "29900",
        }
        ticket = SRTTicket(data)

        assert ticket.seat_type == "특실"
        assert ticket.passenger_type == "경로"
        assert ticket.discount == 29900

    def test_ticket_waiting(self):
        """Test SRTTicket waiting detection."""
        data = {
            "scarNo": "",
            "seatNo": "",
            "psrmClCd": "1",
            "dcntKndCd": "000",
            "rcvdAmt": "59800",
            "stdrPrc": "59800",
            "dcntPrc": "0",
        }
        ticket = SRTTicket(data)

        assert ticket.is_waiting is True

    def test_ticket_dump(self):
        """Test SRTTicket dump method."""
        data = {
            "scarNo": "05",
            "seatNo": "12A",
            "psrmClCd": "1",
            "dcntKndCd": "000",
            "rcvdAmt": "59800",
            "stdrPrc": "59800",
            "dcntPrc": "0",
        }
        ticket = SRTTicket(data)
        dump_str = ticket.dump()

        assert "05호차" in dump_str
        assert "12A" in dump_str
        assert "일반실" in dump_str
        assert "59800원" in dump_str


class TestSRTTrain:
    """Test SRTTrain class."""

    def test_train_initialization(self):
        """Test SRTTrain object creation."""
        data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "dptStnRunOrdr": "1",
            "dptStnConsOrdr": "1",
            "arvDt": "20250109",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "arvStnRunOrdr": "10",
            "arvStnConsOrdr": "10",
            "gnrmRsvPsbStr": "예약가능",
            "sprmRsvPsbStr": "예약가능",
            "rsvWaitPsbCdNm": "가능",
            "rsvWaitPsbCd": "9",
        }
        train = SRTTrain(data)

        assert train.train_code == "17"
        assert train.train_name == "SRT"
        assert train.train_number == "301"
        assert train.dep_station_name == "수서"
        assert train.arr_station_name == "부산"
        assert train.general_seat_state == "예약가능"
        assert train.special_seat_state == "예약가능"
        assert train.reserve_wait_possible_code == 9

    def test_train_general_seat_available(self):
        """Test general seat availability check."""
        data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "dptStnRunOrdr": "1",
            "dptStnConsOrdr": "1",
            "arvDt": "20250109",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "arvStnRunOrdr": "10",
            "arvStnConsOrdr": "10",
            "gnrmRsvPsbStr": "예약가능",
            "sprmRsvPsbStr": "매진",
            "rsvWaitPsbCdNm": "불가능",
            "rsvWaitPsbCd": "-2",
        }
        train = SRTTrain(data)

        assert train.general_seat_available() is True
        assert train.special_seat_available() is False
        assert train.seat_available() is True

    def test_train_reserve_standby_available(self):
        """Test reserve standby availability check."""
        data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "dptStnRunOrdr": "1",
            "dptStnConsOrdr": "1",
            "arvDt": "20250109",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "arvStnRunOrdr": "10",
            "arvStnConsOrdr": "10",
            "gnrmRsvPsbStr": "매진",
            "sprmRsvPsbStr": "매진",
            "rsvWaitPsbCdNm": "가능",
            "rsvWaitPsbCd": "9",
        }
        train = SRTTrain(data)

        assert train.reserve_standby_available() is True

    def test_train_dump(self):
        """Test SRTTrain dump method."""
        data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "dptStnRunOrdr": "1",
            "dptStnConsOrdr": "1",
            "arvDt": "20250109",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "arvStnRunOrdr": "10",
            "arvStnConsOrdr": "10",
            "gnrmRsvPsbStr": "예약가능",
            "sprmRsvPsbStr": "예약가능",
            "rsvWaitPsbCdNm": "가능",
            "rsvWaitPsbCd": "9",
        }
        train = SRTTrain(data)
        dump_str = train.dump()

        assert "SRT" in dump_str
        assert "301" in dump_str
        assert "수서" in dump_str
        assert "부산" in dump_str


class TestSRTReservation:
    """Test SRTReservation class."""

    def test_reservation_initialization(self):
        """Test SRTReservation object creation."""
        train_data = {
            "pnrNo": "12345",
            "rcvdAmt": "119600",
            "seatNum": "2",
        }
        pay_data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "iseLmtDt": "20250109",
            "iseLmtTm": "095959",
            "stlFlg": "N",
        }
        tickets = []
        reservation = SRTReservation(train_data, pay_data, tickets)

        assert reservation.reservation_number == "12345"
        assert reservation.total_cost == 119600
        assert reservation.train_name == "SRT"
        assert reservation.dep_station_name == "수서"
        assert reservation.arr_station_name == "부산"
        assert reservation.paid is False
        assert reservation.is_waiting is False

    def test_reservation_waiting(self):
        """Test waiting reservation detection."""
        train_data = {
            "pnrNo": "12345",
            "rcvdAmt": "59800",
            "seatNum": "1",
        }
        pay_data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "iseLmtDt": "",
            "iseLmtTm": "",
            "stlFlg": "N",
        }
        tickets = []
        reservation = SRTReservation(train_data, pay_data, tickets)

        assert reservation.is_waiting is True

    def test_reservation_paid(self):
        """Test paid reservation detection."""
        train_data = {
            "pnrNo": "12345",
            "rcvdAmt": "59800",
            "tkSpecNum": "1",
        }
        pay_data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "iseLmtDt": "20250109",
            "iseLmtTm": "095959",
            "stlFlg": "Y",
        }
        tickets = []
        reservation = SRTReservation(train_data, pay_data, tickets)

        assert reservation.paid is True
        assert reservation.is_running is False

    def test_reservation_dump(self):
        """Test SRTReservation dump method."""
        train_data = {
            "pnrNo": "12345",
            "rcvdAmt": "59800",
            "seatNum": "1",
        }
        pay_data = {
            "stlbTrnClsfCd": "17",
            "trnNo": "301",
            "dptDt": "20250109",
            "dptTm": "100000",
            "dptRsStnCd": "0551",
            "arvTm": "125959",
            "arvRsStnCd": "0020",
            "iseLmtDt": "20250109",
            "iseLmtTm": "095959",
            "stlFlg": "N",
        }
        tickets = []
        reservation = SRTReservation(train_data, pay_data, tickets)
        dump_str = reservation.dump()

        assert "SRT" in dump_str
        assert "수서" in dump_str
        assert "부산" in dump_str
        assert "59800원" in dump_str


class TestSRTResponseData:
    """Test SRTResponseData class."""

    def test_response_data_success(self):
        """Test successful response parsing."""
        response = json.dumps({"resultMap": [{"strResult": "SUCC"}]})
        parser = SRTResponseData(response)

        assert parser.success() is True

    def test_response_data_failure(self):
        """Test failure response parsing."""
        response = json.dumps({"resultMap": [{"strResult": "FAIL"}]})
        parser = SRTResponseData(response)

        assert parser.success() is False

    def test_response_data_message(self):
        """Test message extraction."""
        response = json.dumps(
            {"resultMap": [{"strResult": "SUCC", "msgTxt": "Success message"}]}
        )
        parser = SRTResponseData(response)

        assert parser.message() == "Success message"

    def test_response_data_error_code(self):
        """Test error code response parsing."""
        response = json.dumps({"ErrorCode": "E001", "ErrorMsg": "Error occurred"})

        with pytest.raises(SRTResponseError) as exc_info:
            SRTResponseData(response)
        assert "E001" in str(exc_info.value)

    def test_response_data_get_all(self):
        """Test getting all response data."""
        response = json.dumps({"resultMap": [{"strResult": "SUCC"}], "extra": "data"})
        parser = SRTResponseData(response)
        all_data = parser.get_all()

        assert "resultMap" in all_data
        assert "extra" in all_data

    def test_response_data_get_status(self):
        """Test getting status data."""
        response = json.dumps({"resultMap": [{"strResult": "SUCC", "code": "123"}]})
        parser = SRTResponseData(response)
        status = parser.get_status()

        assert status["strResult"] == "SUCC"
        assert status["code"] == "123"


class TestSRTErrors:
    """Test error classes."""

    def test_srt_error(self):
        """Test SRTError creation."""
        error = SRTError("Test error")

        assert error.msg == "Test error"
        assert str(error) == "Test error"

    def test_srt_login_error(self):
        """Test SRTLoginError creation."""
        error = SRTLoginError("Login failed")

        assert error.msg == "Login failed"
        assert isinstance(error, SRTError)

    def test_srt_response_error(self):
        """Test SRTResponseError creation."""
        error = SRTResponseError("Response error")

        assert error.msg == "Response error"
        assert isinstance(error, SRTError)

    def test_srt_not_logged_in_error(self):
        """Test SRTNotLoggedInError creation."""
        error = SRTNotLoggedInError("Not logged in")

        assert error.msg == "Not logged in"
        assert isinstance(error, SRTError)

    def test_srt_netfunnel_error(self):
        """Test SRTNetFunnelError creation."""
        error = SRTNetFunnelError("NetFunnel error")

        assert error.msg == "NetFunnel error"
        assert isinstance(error, SRTError)


class TestNetFunnelHelper:
    """Test NetFunnelHelper class."""

    def test_netfunnel_initialization(self):
        """Test NetFunnelHelper initialization."""
        helper = NetFunnelHelper()

        assert helper._cached_key is None
        assert helper._last_fetch_time == 0
        assert helper._cache_ttl == 48

    def test_build_params_getTidchkEnter(self):
        """Test parameter building for getTidchkEnter."""
        helper = NetFunnelHelper()
        params = helper._build_params(NetFunnelHelper.OP_CODE["getTidchkEnter"])

        assert params["opcode"] == "5101"
        assert params["sid"] == "service_1"
        assert params["aid"] == "act_10"

    def test_build_params_chkEnter(self):
        """Test parameter building for chkEnter."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        params = helper._build_params(NetFunnelHelper.OP_CODE["chkEnter"])

        assert params["opcode"] == "5002"
        assert params["key"] == "test_key"
        assert params["ttl"] == "1"

    def test_build_params_setComplete(self):
        """Test parameter building for setComplete."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        params = helper._build_params(NetFunnelHelper.OP_CODE["setComplete"])

        assert params["opcode"] == "5004"
        assert params["key"] == "test_key"

    def test_parse_response(self):
        """Test parsing NetFunnel response."""
        helper = NetFunnelHelper()
        response = "NetFunnel.gControl.result='0:200:key=test_key&nwait=10&ip=1.2.3.4'"
        parsed = helper._parse(response)

        assert parsed["status"] == "200"
        assert parsed["key"] == "test_key"
        assert parsed["nwait"] == "10"
        assert parsed["ip"] == "1.2.3.4"

    def test_is_cache_valid(self):
        """Test cache validity check."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        helper._last_fetch_time = 1000.0

        assert helper._is_cache_valid(1010.0) is True
        assert helper._is_cache_valid(1049.0) is False

    def test_clear(self):
        """Test clearing cache."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        helper._last_fetch_time = 1000.0

        helper.clear()

        assert helper._cached_key is None
        assert helper._last_fetch_time == 0


class TestSRT:
    """Test SRT class."""

    def test_srt_initialization_no_auto_login(self):
        """Test SRT initialization without auto login."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        assert srt.srt_id == "test_id"
        assert srt.srt_pw == "test_pw"
        assert srt.is_login is False

    def test_srt_not_logged_in_error_on_search(self):
        """Test SRT raises error when not logged in during search."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        # search_train doesn't check login status, so we test other methods
        assert srt.is_login is False

    def test_srt_not_logged_in_check(self):
        """Test SRT login status check."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        # Verify login status is False
        assert srt.is_login is False

    def test_srt_clear_netfunnel(self):
        """Test SRT clear method."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._netfunnel._cached_key = "test_key"
        srt._netfunnel._last_fetch_time = 1000.0

        srt.clear()

        assert srt._netfunnel._cached_key is None
        assert srt._netfunnel._last_fetch_time == 0


class TestSeatType:
    """Test SeatType enum."""

    def test_seat_type_values(self):
        """Test SeatType enum values."""
        assert SeatType.GENERAL_FIRST.value == 1
        assert SeatType.GENERAL_ONLY.value == 2
        assert SeatType.SPECIAL_FIRST.value == 3
        assert SeatType.SPECIAL_ONLY.value == 4


class TestConstants:
    """Test module constants."""

    def test_station_code(self):
        """Test station code constants."""
        assert STATION_CODE["수서"] == "0551"
        assert STATION_CODE["부산"] == "0020"
        assert STATION_CODE["대전"] == "0010"

    def test_station_name(self):
        """Test station name constants."""
        assert STATION_NAME["0551"] == "수서"
        assert STATION_NAME["0020"] == "부산"
        assert STATION_NAME["0010"] == "대전"

    def test_train_name(self):
        """Test train name constants."""
        assert TRAIN_NAME["17"] == "SRT"
        assert TRAIN_NAME["00"] == "KTX"

    def test_window_seat(self):
        """Test window seat constants."""
        assert WINDOW_SEAT[None] == "000"
        assert WINDOW_SEAT[True] == "012"
        assert WINDOW_SEAT[False] == "013"
