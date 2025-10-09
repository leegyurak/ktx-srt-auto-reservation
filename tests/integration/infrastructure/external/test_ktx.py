"""Integration tests for KTX external module using mocking."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from src.infrastructure.external.ktx import (
    Korail,
    Train,
    AdultPassenger,
    ChildPassenger,
    NoResultsError,
    KorailError,
    TrainType,
)


class TestKorailAuthenticationIntegration:
    """Test Korail authentication flow with mocking."""

    @patch("src.infrastructure.external.ktx.Korail._Korail__enc_password")
    def test_login_flow(self, mock_enc_password):
        """Test complete login flow."""
        mock_enc_password.return_value = "encrypted_password"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "SUCC",
            "strMbCrdNo": "12345678",
            "strCustNm": "홍길동",
            "strEmailAdr": "test@example.com",
            "strCpNo": "010-1234-5678"
        })
        mock_session.post.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session

        result = korail.login()

        assert result is True
        assert korail.logined is True
        assert korail.membership_number == "12345678"
        assert korail.name == "홍길동"

    def test_login_failure_flow(self):
        """Test login failure handling."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "FAIL",
            "h_msg_cd": "P100",
            "h_msg_txt": "Login failed"
        })
        mock_session.post.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session

        result = korail.login()

        assert result is False
        assert korail.logined is False

    def test_logout_flow(self):
        """Test logout flow."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = "OK"
        mock_session.get.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.logined = True

        korail.logout()

        assert korail.logined is False


class TestKorailTrainSearchIntegration:
    """Test Korail train search flow with mocking."""

    def test_search_train_flow(self):
        """Test complete train search flow."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "SUCC",
            "trn_infos": {
                "trn_info": [
                    {
                        "h_trn_clsf_cd": "100",
                        "h_trn_clsf_nm": "KTX",
                        "h_trn_gp_cd": "300",
                        "h_trn_no": "001",
                        "h_expct_dlay_hr": "000",
                        "h_dpt_rs_stn_nm": "서울",
                        "h_dpt_rs_stn_cd": "0001",
                        "h_dpt_dt": "20250110",
                        "h_dpt_tm": "100000",
                        "h_arv_rs_stn_nm": "부산",
                        "h_arv_rs_stn_cd": "0020",
                        "h_arv_dt": "20250110",
                        "h_arv_tm": "125959",
                        "h_run_dt": "20250110",
                        "h_rsv_psb_flg": "Y",
                        "h_spe_rsv_cd": "11",
                        "h_gen_rsv_cd": "11",
                        "h_wait_rsv_flg": "0",
                    }
                ]
            }
        })
        mock_session.get.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.membership_number = "12345678"

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = korail.search_train(dep="서울", arr="부산", date=tomorrow)

        assert len(trains) == 1
        assert isinstance(trains[0], Train)
        assert trains[0].train_type_name == "KTX"
        assert trains[0].dep_name == "서울"
        assert trains[0].arr_name == "부산"

    def test_search_train_with_passengers_flow(self):
        """Test train search with multiple passengers."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "SUCC",
            "trn_infos": {
                "trn_info": [
                    {
                        "h_trn_clsf_cd": "100",
                        "h_trn_clsf_nm": "KTX",
                        "h_trn_gp_cd": "300",
                        "h_trn_no": "001",
                        "h_dpt_rs_stn_nm": "서울",
                        "h_dpt_rs_stn_cd": "0001",
                        "h_dpt_dt": "20250110",
                        "h_dpt_tm": "100000",
                        "h_arv_rs_stn_nm": "부산",
                        "h_arv_rs_stn_cd": "0020",
                        "h_arv_dt": "20250110",
                        "h_arv_tm": "125959",
                        "h_run_dt": "20250110",
                        "h_spe_rsv_cd": "11",
                        "h_gen_rsv_cd": "11",
                        "h_wait_rsv_flg": "0",
                    }
                ]
            }
        })
        mock_session.get.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.membership_number = "12345678"

        passengers = [AdultPassenger(count=2), ChildPassenger(count=1)]
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = korail.search_train(
            dep="서울", arr="부산", date=tomorrow, passengers=passengers
        )

        assert len(trains) == 1

    def test_search_train_no_results_flow(self):
        """Test train search with no results."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "FAIL",
            "h_msg_cd": "P100",
            "h_msg_txt": "No results found"
        })
        mock_session.get.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.membership_number = "12345678"

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

        with pytest.raises(NoResultsError):
            korail.search_train(dep="서울", arr="부산", date=tomorrow)


class TestKorailReservationIntegration:
    """Test Korail reservation flow with mocking."""

    def test_get_reservations_flow(self):
        """Test getting reservations."""
        # Mock myreservationview response
        view_response = Mock()
        view_response.text = json.dumps({
            "strResult": "SUCC",
            "jrny_infos": {
                "jrny_info": [
                    {
                        "train_infos": {
                            "train_info": [
                                {
                                    "h_trn_clsf_cd": "100",
                                    "h_trn_clsf_nm": "KTX",
                                    "h_trn_gp_cd": "300",
                                    "h_trn_no": "001",
                                    "h_dpt_rs_stn_nm": "서울",
                                    "h_dpt_rs_stn_cd": "0001",
                                    "h_dpt_dt": "20250110",
                                    "h_dpt_tm": "100000",
                                    "h_arv_rs_stn_nm": "부산",
                                    "h_arv_rs_stn_cd": "0020",
                                    "h_arv_dt": "20250110",
                                    "h_arv_tm": "125959",
                                    "h_run_dt": "20250110",
                                    "h_pnr_no": "12345",
                                    "h_tot_seat_cnt": "2",
                                    "h_ntisu_lmt_dt": "20250110",
                                    "h_ntisu_lmt_tm": "095959",
                                    "h_rsv_amt": "119600",
                                }
                            ]
                        }
                    }
                ]
            }
        })

        # Mock myreservationlist response
        list_response = Mock()
        list_response.text = json.dumps({
            "strResult": "SUCC",
            "h_wct_no": "001",
            "jrny_infos": {
                "jrny_info": [
                    {
                        "seat_infos": {
                            "seat_info": [
                                {
                                    "h_srcar_no": "05",
                                    "h_seat_no": "12A",
                                    "h_psrm_cl_nm": "일반실",
                                    "h_psg_tp_dv_nm": "어른",
                                    "h_rcvd_amt": "59800",
                                    "h_seat_prc": "59800",
                                    "h_dcnt_amt": "0",
                                }
                            ]
                        }
                    }
                ]
            }
        })

        mock_session = Mock()
        mock_session.get.side_effect = [view_response, list_response]

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.membership_number = "12345678"

        reservations = korail.reservations()

        assert len(reservations) == 1
        assert reservations[0].rsv_id == "12345"
        assert reservations[0].price == 119600

    def test_get_tickets_flow(self):
        """Test getting tickets."""
        # Mock myticketlist response
        list_response = Mock()
        list_response.text = json.dumps({
            "strResult": "SUCC",
            "reservation_list": [
                {
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
                                    "h_dpt_dt": "20250110",
                                    "h_dpt_tm": "100000",
                                    "h_arv_rs_stn_nm": "부산",
                                    "h_arv_rs_stn_cd": "0020",
                                    "h_arv_dt": "20250110",
                                    "h_arv_tm": "125959",
                                    "h_run_dt": "20250110",
                                    "h_seat_no_end": "02",
                                    "h_seat_cnt": "1",
                                    "h_buy_ps_nm": "홍길동",
                                    "h_orgtk_sale_dt": "20250109",
                                    "h_pnr_no": "12345",
                                    "h_orgtk_wct_no": "0001",
                                    "h_orgtk_ret_sale_dt": "20250109",
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
            ]
        })

        # Mock myticketseat response
        seat_response = Mock()
        seat_response.text = json.dumps({
            "strResult": "SUCC",
            "ticket_infos": {
                "ticket_info": [
                    {
                        "tk_seat_info": [
                            {
                                "h_seat_no": "01"
                            }
                        ]
                    }
                ]
            }
        })

        mock_session = Mock()
        mock_session.get.side_effect = [list_response, seat_response]

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session

        tickets = korail.tickets()

        assert len(tickets) == 1
        assert tickets[0].buyer_name == "홍길동"
        assert tickets[0].price == 59800


class TestKorailErrorHandlingIntegration:
    """Test Korail error handling in integration scenarios."""

    def test_error_propagation_in_search(self):
        """Test that errors propagate correctly in search flow."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "strResult": "FAIL",
            "h_msg_cd": "E999",
            "h_msg_txt": "Unknown error occurred"
        })
        mock_session.get.return_value = mock_response

        korail = Korail(korail_id="test_id", korail_pw="test_pw", auto_login=False)
        korail._session = mock_session
        korail.membership_number = "12345678"

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

        with pytest.raises(KorailError) as exc_info:
            korail.search_train(dep="서울", arr="부산", date=tomorrow)

        assert exc_info.value.msg == "Unknown error occurred"
        assert exc_info.value.code == "E999"
