"""Unit tests for domain enums"""
import pytest
from src.domain.models.enums import PassengerType, TrainType


@pytest.mark.unit
@pytest.mark.domain
class TestPassengerType:
    """Tests for PassengerType enum"""

    def test_passenger_type_values(self):
        """Test that PassengerType has correct values"""
        assert PassengerType.ADULT.value == "adult"
        assert PassengerType.CHILD.value == "child"
        assert PassengerType.SENIOR.value == "senior"

    def test_passenger_type_members(self):
        """Test that PassengerType has all expected members"""
        passenger_types = list(PassengerType)
        assert len(passenger_types) == 3
        assert PassengerType.ADULT in passenger_types
        assert PassengerType.CHILD in passenger_types
        assert PassengerType.SENIOR in passenger_types

    def test_passenger_type_by_value(self):
        """Test accessing PassengerType by value"""
        assert PassengerType("adult") == PassengerType.ADULT
        assert PassengerType("child") == PassengerType.CHILD
        assert PassengerType("senior") == PassengerType.SENIOR

    def test_passenger_type_invalid_value(self):
        """Test that invalid value raises ValueError"""
        with pytest.raises(ValueError):
            PassengerType("invalid")

    def test_passenger_type_equality(self):
        """Test PassengerType equality"""
        assert PassengerType.ADULT == PassengerType.ADULT
        assert PassengerType.CHILD == PassengerType.CHILD
        assert PassengerType.ADULT != PassengerType.CHILD

    def test_passenger_type_string_representation(self):
        """Test PassengerType string representation"""
        assert str(PassengerType.ADULT) == "PassengerType.ADULT"
        assert PassengerType.ADULT.name == "ADULT"


@pytest.mark.unit
@pytest.mark.domain
class TestTrainType:
    """Tests for TrainType enum"""

    def test_train_type_values(self):
        """Test that TrainType has correct values"""
        assert TrainType.KTX.value == "ktx"
        assert TrainType.SRT.value == "srt"

    def test_train_type_members(self):
        """Test that TrainType has all expected members"""
        train_types = list(TrainType)
        assert len(train_types) == 2
        assert TrainType.KTX in train_types
        assert TrainType.SRT in train_types

    def test_train_type_by_value(self):
        """Test accessing TrainType by value"""
        assert TrainType("ktx") == TrainType.KTX
        assert TrainType("srt") == TrainType.SRT

    def test_train_type_invalid_value(self):
        """Test that invalid value raises ValueError"""
        with pytest.raises(ValueError):
            TrainType("mugunghwa")

    def test_train_type_equality(self):
        """Test TrainType equality"""
        assert TrainType.KTX == TrainType.KTX
        assert TrainType.SRT == TrainType.SRT
        assert TrainType.KTX != TrainType.SRT

    def test_train_type_string_representation(self):
        """Test TrainType string representation"""
        assert str(TrainType.KTX) == "TrainType.KTX"
        assert TrainType.KTX.name == "KTX"

    def test_train_type_contains_ktx(self):
        """Test that TrainType contains KTX"""
        assert TrainType.KTX in TrainType

    def test_train_type_contains_srt(self):
        """Test that TrainType contains SRT"""
        assert TrainType.SRT in TrainType
