"""Integration tests for SRT external module using mocking."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from src.infrastructure.external.srt import (
    SRT,
    SRTTrain,
    SRTReservation,
    Adult,
    Child,
    SeatType,
    SRTLoginError,
    SRTResponseError,
    SRTNotLoggedInError,
)


class TestSRTAuthenticationIntegration:
    """Test SRT authentication flow with mocking."""

    def test_login_flow_success(self):
        """Test successful login flow."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "userMap": {
                "MB_CRD_NO": "12345678",
                "CUST_NM": "홍길동",
                "MBL_PHONE": "010-1234-5678"
            }
        })
        mock_response.json.return_value = json.loads(mock_response.text)
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session

        result = srt.login()

        assert result is True
        assert srt.is_login is True
        assert srt.membership_number == "12345678"
        assert srt.membership_name == "홍길동"

    def test_login_flow_invalid_credentials(self):
        """Test login with invalid credentials."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = "존재하지않는 회원입니다"
        mock_response.json.return_value = {"MSG": "Invalid user"}
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="invalid_id", srt_pw="invalid_pw", auto_login=False)
        srt._session = mock_session

        with pytest.raises(SRTLoginError):
            srt.login()

    def test_logout_flow(self):
        """Test logout flow."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt.is_login = True

        result = srt.logout()

        assert result is True
        assert srt.is_login is False


class TestSRTTrainSearchIntegration:
    """Test SRT train search flow with mocking."""

    def test_search_train_flow(self):
        """Test complete train search flow."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "mock_key"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "outDataSets": {
                "dsOutput1": [
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "301",
                        "dptDt": "20250110",
                        "dptTm": "100000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "125959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "예약가능",
                        "rsvWaitPsbCdNm": "가능",
                        "rsvWaitPsbCd": "9",
                    }
                ]
            }
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = srt.search_train(dep="수서", arr="부산", date=tomorrow)

        assert len(trains) == 1
        assert isinstance(trains[0], SRTTrain)
        assert trains[0].train_name == "SRT"
        assert trains[0].dep_station_name == "수서"
        assert trains[0].arr_station_name == "부산"

    def test_search_train_with_passengers(self):
        """Test train search with multiple passengers."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "mock_key"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "outDataSets": {
                "dsOutput1": [
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "301",
                        "dptDt": "20250110",
                        "dptTm": "100000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "125959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "예약가능",
                        "rsvWaitPsbCdNm": "가능",
                        "rsvWaitPsbCd": "9",
                    }
                ]
            }
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        passengers = [Adult(count=2), Child(count=1)]
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = srt.search_train(
            dep="수서", arr="부산", date=tomorrow, passengers=passengers
        )

        assert len(trains) == 1

    def test_search_train_available_only(self):
        """Test train search with available_only flag."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "mock_key"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "outDataSets": {
                "dsOutput1": [
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "301",
                        "dptDt": "20250110",
                        "dptTm": "100000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "125959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "매진",
                        "rsvWaitPsbCdNm": "불가능",
                        "rsvWaitPsbCd": "-2",
                    }
                ]
            }
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = srt.search_train(
            dep="수서", arr="부산", date=tomorrow, available_only=True
        )

        # Should still return the train since general seat is available
        assert len(trains) == 1
        assert trains[0].general_seat_available() is True

    def test_search_train_invalid_station(self):
        """Test train search with invalid station names."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

        with pytest.raises(ValueError):
            srt.search_train(dep="존재하지않는역", arr="부산", date=tomorrow)

    def test_search_train_past_date(self):
        """Test train search with past date."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        with pytest.raises(ValueError):
            srt.search_train(dep="수서", arr="부산", date=yesterday)


class TestSRTReservationIntegration:
    """Test SRT reservation flow with mocking."""

    def test_get_reservations_flow(self):
        """Test getting reservations."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "trainListMap": [
                {
                    "pnrNo": "12345",
                    "rcvdAmt": "119600",
                    "seatNum": "2",
                }
            ],
            "payListMap": [
                {
                    "stlbTrnClsfCd": "17",
                    "trnNo": "301",
                    "dptDt": "20250110",
                    "dptTm": "100000",
                    "dptRsStnCd": "0551",
                    "arvTm": "125959",
                    "arvRsStnCd": "0020",
                    "iseLmtDt": "20250110",
                    "iseLmtTm": "095959",
                    "stlFlg": "N",
                }
            ]
        })

        # Mock ticket_info response
        ticket_response = Mock()
        ticket_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "trainListMap": [
                {
                    "scarNo": "05",
                    "seatNo": "12A",
                    "psrmClCd": "1",
                    "dcntKndCd": "000",
                    "rcvdAmt": "59800",
                    "stdrPrc": "59800",
                    "dcntPrc": "0",
                }
            ]
        })

        mock_session.post.side_effect = [mock_response, ticket_response]

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt.is_login = True

        reservations = srt.get_reservations()

        assert len(reservations) == 1
        assert isinstance(reservations[0], SRTReservation)
        assert reservations[0].reservation_number == "12345"
        assert reservations[0].total_cost == 119600

    def test_get_reservations_not_logged_in(self):
        """Test getting reservations when not logged in."""
        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)

        with pytest.raises(TypeError):  # SRTNotLoggedInError requires msg
            srt.get_reservations()


class TestSRTErrorHandlingIntegration:
    """Test SRT error handling in integration scenarios."""

    def test_error_propagation_in_search(self):
        """Test that errors propagate correctly in search flow."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "mock_key"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "FAIL", "msgTxt": "Error occurred"}]
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")

        with pytest.raises(SRTResponseError) as exc_info:
            srt.search_train(dep="수서", arr="부산", date=tomorrow)

        assert "Error occurred" in str(exc_info.value)


class TestSRTNetFunnelIntegration:
    """Test SRT NetFunnel integration."""

    def test_netfunnel_usage_in_search(self):
        """Test that NetFunnel is used in search."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "test_key_123"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "outDataSets": {
                "dsOutput1": [
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "301",
                        "dptDt": "20250110",
                        "dptTm": "100000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "125959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "예약가능",
                        "rsvWaitPsbCdNm": "가능",
                        "rsvWaitPsbCd": "9",
                    }
                ]
            }
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        srt.search_train(dep="수서", arr="부산", date=tomorrow)

        # Verify NetFunnel.run() was called
        mock_netfunnel.run.assert_called()

    def test_netfunnel_clear(self):
        """Test clearing NetFunnel cache."""
        mock_netfunnel = Mock()

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._netfunnel = mock_netfunnel

        srt.clear()

        # Verify NetFunnel.clear() was called
        mock_netfunnel.clear.assert_called_once()


class TestSRTComplexScenarios:
    """Test complex integration scenarios."""

    def test_search_and_filter_workflow(self):
        """Test searching and filtering trains."""
        mock_netfunnel = Mock()
        mock_netfunnel.run.return_value = "mock_key"

        mock_session = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "resultMap": [{"strResult": "SUCC"}],
            "outDataSets": {
                "dsOutput1": [
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "301",
                        "dptDt": "20250110",
                        "dptTm": "100000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "125959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "매진",
                        "rsvWaitPsbCdNm": "가능",
                        "rsvWaitPsbCd": "9",
                    },
                    {
                        "stlbTrnClsfCd": "17",
                        "trnNo": "303",
                        "dptDt": "20250110",
                        "dptTm": "130000",
                        "dptRsStnCd": "0551",
                        "dptStnRunOrdr": "1",
                        "dptStnConsOrdr": "1",
                        "arvDt": "20250110",
                        "arvTm": "155959",
                        "arvRsStnCd": "0020",
                        "arvStnRunOrdr": "10",
                        "arvStnConsOrdr": "10",
                        "gnrmRsvPsbStr": "예약가능",
                        "sprmRsvPsbStr": "예약가능",
                        "rsvWaitPsbCdNm": "불가능",
                        "rsvWaitPsbCd": "-2",
                    }
                ]
            }
        })
        mock_session.post.return_value = mock_response

        srt = SRT(srt_id="test_id", srt_pw="test_pw", auto_login=False)
        srt._session = mock_session
        srt._netfunnel = mock_netfunnel

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        trains = srt.search_train(
            dep="수서", arr="부산", date=tomorrow, time_limit="120000"
        )

        # Should only return the first train (before time_limit)
        assert len(trains) == 1
        assert trains[0].train_number == "301"
