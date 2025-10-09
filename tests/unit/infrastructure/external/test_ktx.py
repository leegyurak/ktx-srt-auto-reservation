"""Unit tests for KTX external module."""

import pytest

from src.infrastructure.external.ktx import (
    Korail,
    Train,
    Schedule,
    Ticket,
    Reservation,
    Seat,
    AdultPassenger,
    ChildPassenger,
    SeniorPassenger,
    Passenger,
    KorailError,
    NeedToLoginError,
    NoResultsError,
    SoldOutError,
    NetFunnelHelper,
    TrainType,
    ReserveOption,
)


class TestSchedule:
    """Test Schedule class."""

    def test_schedule_initialization(self):
        """Test Schedule object creation."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_expct_dlay_hr": "000",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
        }
        schedule = Schedule(data)

        assert schedule.train_type == "100"
        assert schedule.train_type_name == "KTX"
        assert schedule.dep_name == "서울"
        assert schedule.dep_code == "0001"
        assert schedule.arr_name == "부산"
        assert schedule.arr_code == "0020"

    def test_schedule_repr(self):
        """Test Schedule string representation."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_expct_dlay_hr": "000",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
        }
        schedule = Schedule(data)
        repr_str = repr(schedule)

        assert "KTX" in repr_str
        assert "001" in repr_str
        assert "서울" in repr_str
        assert "부산" in repr_str


class TestTrain:
    """Test Train class."""

    def test_train_initialization(self):
        """Test Train object creation with seat info."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_expct_dlay_hr": "000",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_rsv_psb_flg": "Y",
            "h_rsv_psb_nm": "예약가능",
            "h_spe_rsv_cd": "11",
            "h_gen_rsv_cd": "11",
            "h_wait_rsv_flg": "9",
        }
        train = Train(data)

        assert train.reserve_possible == "Y"
        assert train.special_seat == "11"
        assert train.general_seat == "11"
        assert train.wait_reserve_flag == 9

    def test_has_special_seat(self):
        """Test special seat availability check."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_spe_rsv_cd": "11",
            "h_gen_rsv_cd": "00",
            "h_wait_rsv_flg": "0",
        }
        train = Train(data)

        assert train.has_special_seat() is True
        assert train.has_general_seat() is False
        assert train.has_seat() is True

    def test_has_general_seat(self):
        """Test general seat availability check."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_spe_rsv_cd": "00",
            "h_gen_rsv_cd": "11",
            "h_wait_rsv_flg": "0",
        }
        train = Train(data)

        assert train.has_general_seat() is True
        assert train.has_special_seat() is False

    def test_has_waiting_list(self):
        """Test waiting list availability check."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_spe_rsv_cd": "00",
            "h_gen_rsv_cd": "00",
            "h_wait_rsv_flg": "9",
        }
        train = Train(data)

        assert train.has_general_waiting_list() is True
        assert train.has_waiting_list() is True


class TestTicket:
    """Test Ticket class."""

    def test_ticket_initialization(self):
        """Test Ticket object creation."""
        data = {
            "ticket_list": [
                {
                    "train_info": [
                        {
                            "h_trn_clsf_cd": "100",
                            "h_trn_clsf_nm": "KTX",
                            "h_trn_gp_cd": "300",
                            "h_trn_no": "001",
                            "h_dpt_rs_stn_nm": "서울",
                            "h_dpt_rs_stn_cd": "0001",
                            "h_dpt_dt": "20250109",
                            "h_dpt_tm": "100000",
                            "h_arv_rs_stn_nm": "부산",
                            "h_arv_rs_stn_cd": "0020",
                            "h_arv_dt": "20250109",
                            "h_arv_tm": "125959",
                            "h_run_dt": "20250109",
                            "h_seat_no_end": "02",
                            "h_seat_cnt": "1",
                            "h_buy_ps_nm": "홍길동",
                            "h_orgtk_sale_dt": "20250108",
                            "h_pnr_no": "12345",
                            "h_orgtk_wct_no": "0001",
                            "h_orgtk_ret_sale_dt": "20250108",
                            "h_orgtk_sale_sqno": "001",
                            "h_orgtk_ret_pwd": "1234",
                            "h_rcvd_amt": "59800",
                            "h_srcar_no": "05",
                            "h_seat_no": "01",
                        }
                    ]
                }
            ]
        }
        ticket = Ticket(data)

        assert ticket.buyer_name == "홍길동"
        assert ticket.price == 59800
        assert ticket.car_no == "05"
        assert ticket.seat_no == "01"
        assert ticket.pnr_no == "12345"

    def test_get_ticket_no(self):
        """Test ticket number generation."""
        data = {
            "ticket_list": [
                {
                    "train_info": [
                        {
                            "h_trn_clsf_cd": "100",
                            "h_trn_clsf_nm": "KTX",
                            "h_trn_gp_cd": "300",
                            "h_trn_no": "001",
                            "h_dpt_rs_stn_nm": "서울",
                            "h_dpt_rs_stn_cd": "0001",
                            "h_dpt_dt": "20250109",
                            "h_dpt_tm": "100000",
                            "h_arv_rs_stn_nm": "부산",
                            "h_arv_rs_stn_cd": "0020",
                            "h_arv_dt": "20250109",
                            "h_arv_tm": "125959",
                            "h_run_dt": "20250109",
                            "h_seat_no_end": "02",
                            "h_seat_cnt": "1",
                            "h_buy_ps_nm": "홍길동",
                            "h_orgtk_sale_dt": "20250108",
                            "h_pnr_no": "12345",
                            "h_orgtk_wct_no": "0001",
                            "h_orgtk_ret_sale_dt": "20250108",
                            "h_orgtk_sale_sqno": "001",
                            "h_orgtk_ret_pwd": "1234",
                            "h_rcvd_amt": "59800",
                            "h_srcar_no": "05",
                            "h_seat_no": "01",
                        }
                    ]
                }
            ]
        }
        ticket = Ticket(data)

        assert ticket.get_ticket_no() == "0001-20250108-001-1234"


class TestReservation:
    """Test Reservation class."""

    def test_reservation_initialization(self):
        """Test Reservation object creation."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_pnr_no": "12345",
            "h_tot_seat_cnt": "2",
            "h_ntisu_lmt_dt": "20250109",
            "h_ntisu_lmt_tm": "095959",
            "h_rsv_amt": "119600",
            "txtJrnySqno": "001",
            "txtJrnyCnt": "01",
            "hidRsvChgNo": "00000",
        }
        reservation = Reservation(data)

        assert reservation.rsv_id == "12345"
        assert reservation.seat_no_count == 2
        assert reservation.price == 119600
        assert reservation.is_waiting is False

    def test_reservation_waiting(self):
        """Test waiting reservation detection."""
        data = {
            "h_trn_clsf_cd": "100",
            "h_trn_clsf_nm": "KTX",
            "h_trn_gp_cd": "300",
            "h_trn_no": "001",
            "h_dpt_rs_stn_nm": "서울",
            "h_dpt_rs_stn_cd": "0001",
            "h_dpt_dt": "20250109",
            "h_dpt_tm": "100000",
            "h_arv_rs_stn_nm": "부산",
            "h_arv_rs_stn_cd": "0020",
            "h_arv_dt": "20250109",
            "h_arv_tm": "125959",
            "h_run_dt": "20250109",
            "h_pnr_no": "12345",
            "h_tot_seat_cnt": "1",
            "h_ntisu_lmt_dt": "00000000",
            "h_ntisu_lmt_tm": "000000",
            "h_rsv_amt": "59800",
        }
        reservation = Reservation(data)

        assert reservation.is_waiting is True


class TestSeat:
    """Test Seat class."""

    def test_seat_initialization(self):
        """Test Seat object creation."""
        data = {
            "h_srcar_no": "05",
            "h_seat_no": "12A",
            "h_psrm_cl_nm": "일반실",
            "h_psg_tp_dv_nm": "어른",
            "h_rcvd_amt": "59800",
            "h_seat_prc": "59800",
            "h_dcnt_amt": "0",
        }
        seat = Seat(data)

        assert seat.car == "05"
        assert seat.seat == "12A"
        assert seat.seat_type == "일반실"
        assert seat.passenger_type == "어른"
        assert seat.price == 59800
        assert seat.discount == 0
        assert seat.is_waiting is False

    def test_seat_waiting(self):
        """Test waiting seat detection."""
        data = {
            "h_srcar_no": "",
            "h_seat_no": "",
            "h_psrm_cl_nm": "일반실",
            "h_psg_tp_dv_nm": "어른",
            "h_rcvd_amt": "59800",
            "h_seat_prc": "59800",
            "h_dcnt_amt": "0",
        }
        seat = Seat(data)

        assert seat.is_waiting is True


class TestPassenger:
    """Test Passenger classes."""

    def test_adult_passenger(self):
        """Test AdultPassenger creation."""
        passenger = AdultPassenger(count=2)

        assert passenger.typecode == "1"
        assert passenger.count == 2

    def test_child_passenger(self):
        """Test ChildPassenger creation."""
        passenger = ChildPassenger(count=1)

        assert passenger.typecode == "3"
        assert passenger.count == 1

    def test_senior_passenger(self):
        """Test SeniorPassenger creation."""
        passenger = SeniorPassenger(count=1)

        assert passenger.typecode == "1"
        assert passenger.discount_type == "131"

    def test_passenger_addition(self):
        """Test adding passengers of same type."""
        p1 = AdultPassenger(count=2)
        p2 = AdultPassenger(count=1)
        p3 = p1 + p2

        assert p3.count == 3

    def test_passenger_addition_different_type_error(self):
        """Test adding passengers of different types raises error."""
        p1 = AdultPassenger(count=2)
        p2 = ChildPassenger(count=1)

        with pytest.raises(TypeError):
            _ = p1 + p2

    def test_passenger_reduce(self):
        """Test reducing passenger list."""
        passengers = [
            AdultPassenger(count=1),
            AdultPassenger(count=2),
            ChildPassenger(count=1),
        ]
        reduced = Passenger.reduce(passengers)

        assert len(reduced) == 2
        assert any(p.count == 3 and isinstance(p, AdultPassenger) for p in reduced)
        assert any(p.count == 1 and isinstance(p, ChildPassenger) for p in reduced)

    def test_passenger_get_dict(self):
        """Test passenger dictionary generation."""
        passenger = AdultPassenger(count=2)
        data = passenger.get_dict(1)

        assert data["txtPsgTpCd1"] == "1"
        assert data["txtCompaCnt1"] == 2


class TestKorailErrors:
    """Test error classes."""

    def test_korail_error(self):
        """Test KorailError creation."""
        error = KorailError("Test error", "E001")

        assert error.msg == "Test error"
        assert error.code == "E001"
        assert str(error) == "Test error (E001)"

    def test_need_to_login_error(self):
        """Test NeedToLoginError."""
        error = NeedToLoginError("P058")

        assert error.code == "P058"
        assert "P058" in NeedToLoginError.codes

    def test_no_results_error(self):
        """Test NoResultsError."""
        error = NoResultsError("P100")

        assert error.code == "P100"
        assert "P100" in NoResultsError.codes

    def test_sold_out_error(self):
        """Test SoldOutError."""
        error = SoldOutError("ERR211161")

        assert error.code == "ERR211161"
        assert "ERR211161" in SoldOutError.codes


class TestNetFunnelHelper:
    """Test NetFunnelHelper class."""

    def test_netfunnel_initialization(self):
        """Test NetFunnelHelper initialization."""
        helper = NetFunnelHelper()

        assert helper._cached_key is None
        assert helper._last_fetch_time == 0
        assert helper._cache_ttl == 50

    def test_build_params_getTidchkEnter(self):
        """Test parameter building for getTidchkEnter."""
        helper = NetFunnelHelper()
        params = helper._build_params(NetFunnelHelper.OP_CODE["getTidchkEnter"])

        assert params["opcode"] == "5101"
        assert params["sid"] == "service_1"
        assert params["aid"] == "act_8"

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
        response = "200:key=test_key&nwait=10"
        parsed = helper._parse(response)

        assert parsed["status"] == "200"
        assert parsed["key"] == "test_key"
        assert parsed["nwait"] == "10"

    def test_is_cache_valid(self):
        """Test cache validity check."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        helper._last_fetch_time = 1000.0

        assert helper._is_cache_valid(1010.0) is True
        assert helper._is_cache_valid(1051.0) is False

    def test_clear(self):
        """Test clearing cache."""
        helper = NetFunnelHelper()
        helper._cached_key = "test_key"
        helper._last_fetch_time = 1000.0

        helper.clear()

        assert helper._cached_key is None
        assert helper._last_fetch_time == 0


class TestKorail:
    """Test Korail class."""

    def test_korail_initialization_no_auto_login(self):
        """Test Korail initialization without auto login."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        assert korail.korail_id == "test_id"
        assert korail.korail_pw == "test_pw"
        assert korail.logined is False

    def test_result_check_success(self):
        """Test successful result check."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        result = korail._result_check({"strResult": "SUCC"})
        assert result is True

    def test_result_check_no_results_error(self):
        """Test result check raises NoResultsError."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        with pytest.raises(NoResultsError):
            korail._result_check(
                {"strResult": "FAIL", "h_msg_cd": "P100", "h_msg_txt": "No results"}
            )

    def test_result_check_need_login_error(self):
        """Test result check raises NeedToLoginError."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        with pytest.raises(NeedToLoginError):
            korail._result_check(
                {"strResult": "FAIL", "h_msg_cd": "P058", "h_msg_txt": "Need login"}
            )

    def test_result_check_sold_out_error(self):
        """Test result check raises SoldOutError."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        with pytest.raises(SoldOutError):
            korail._result_check(
                {
                    "strResult": "FAIL",
                    "h_msg_cd": "ERR211161",
                    "h_msg_txt": "Sold out",
                }
            )

    def test_result_check_generic_error(self):
        """Test result check raises generic KorailError."""
        korail = Korail(
            korail_id="test_id", korail_pw="test_pw", auto_login=False
        )

        with pytest.raises(KorailError) as exc_info:
            korail._result_check(
                {
                    "strResult": "FAIL",
                    "h_msg_cd": "E999",
                    "h_msg_txt": "Unknown error",
                }
            )
        assert exc_info.value.msg == "Unknown error"
        assert exc_info.value.code == "E999"


class TestTrainType:
    """Test TrainType constants."""

    def test_train_type_values(self):
        """Test TrainType constant values."""
        assert TrainType.KTX == "100"
        assert TrainType.SAEMAEUL == "101"
        assert TrainType.MUGUNGHWA == "102"
        assert TrainType.ALL == "109"


class TestReserveOption:
    """Test ReserveOption constants."""

    def test_reserve_option_values(self):
        """Test ReserveOption constant values."""
        assert ReserveOption.GENERAL_FIRST == "GENERAL_FIRST"
        assert ReserveOption.GENERAL_ONLY == "GENERAL_ONLY"
        assert ReserveOption.SPECIAL_FIRST == "SPECIAL_FIRST"
        assert ReserveOption.SPECIAL_ONLY == "SPECIAL_ONLY"
