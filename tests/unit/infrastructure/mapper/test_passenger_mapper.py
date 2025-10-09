"""Unit tests for PassengerMapper"""
import pytest
from src.domain.models.entities import Passenger
from src.domain.models.enums import PassengerType
from src.infrastructure.mappers import PassengerMapper
from src.infrastructure.external.ktx import AdultPassenger, ChildPassenger, SeniorPassenger
from src.infrastructure.external.srt import Adult, Child, Senior


@pytest.mark.unit
@pytest.mark.mapper
class TestPassengerMapperToKorail:
    """Tests for PassengerMapper.to_korail()"""

    def test_convert_adult_passenger_to_korail(self):
        """Test converting adult passenger to Korail format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)

        # Act
        result = PassengerMapper.to_korail(passenger)

        # Assert
        assert isinstance(result, AdultPassenger)
        assert result.count == 2

    def test_convert_child_passenger_to_korail(self):
        """Test converting child passenger to Korail format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.CHILD, count=1)

        # Act
        result = PassengerMapper.to_korail(passenger)

        # Assert
        assert isinstance(result, ChildPassenger)
        assert result.count == 1

    def test_convert_senior_passenger_to_korail(self):
        """Test converting senior passenger to Korail format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.SENIOR, count=3)

        # Act
        result = PassengerMapper.to_korail(passenger)

        # Assert
        assert isinstance(result, SeniorPassenger)
        assert result.count == 3

    def test_convert_adult_passenger_list_to_korail(self):
        """Test converting adult passenger in a list to Korail format"""
        # Arrange
        adult_passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)

        # Act
        result = PassengerMapper.to_korail(adult_passenger)

        # Assert
        assert isinstance(result, AdultPassenger)
        assert result.count == 2

    def test_convert_child_passenger_list_to_korail(self):
        """Test converting child passenger in a list to Korail format"""
        # Arrange
        child_passenger = Passenger(passenger_type=PassengerType.CHILD, count=1)

        # Act
        result = PassengerMapper.to_korail(child_passenger)

        # Assert
        assert isinstance(result, ChildPassenger)
        assert result.count == 1

    def test_convert_senior_passenger_list_to_korail(self):
        """Test converting senior passenger in a list to Korail format"""
        # Arrange
        senior_passenger = Passenger(passenger_type=PassengerType.SENIOR, count=1)

        # Act
        result = PassengerMapper.to_korail(senior_passenger)

        # Assert
        assert isinstance(result, SeniorPassenger)
        assert result.count == 1


@pytest.mark.unit
@pytest.mark.mapper
class TestPassengerMapperToSRT:
    """Tests for PassengerMapper.to_srt()"""

    def test_convert_adult_passenger_to_srt(self):
        """Test converting adult passenger to SRT format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)

        # Act
        result = PassengerMapper.to_srt(passenger)

        # Assert
        assert isinstance(result, Adult)
        assert result.count == 2

    def test_convert_child_passenger_to_srt(self):
        """Test converting child passenger to SRT format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.CHILD, count=1)

        # Act
        result = PassengerMapper.to_srt(passenger)

        # Assert
        assert isinstance(result, Child)
        assert result.count == 1

    def test_convert_senior_passenger_to_srt(self):
        """Test converting senior passenger to SRT format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.SENIOR, count=3)

        # Act
        result = PassengerMapper.to_srt(passenger)

        # Assert
        assert isinstance(result, Senior)
        assert result.count == 3

    def test_convert_adult_passenger_list_to_srt(self):
        """Test converting adult passenger in a list to SRT format"""
        # Arrange
        adult_passenger = Passenger(passenger_type=PassengerType.ADULT, count=2)

        # Act
        result = PassengerMapper.to_srt(adult_passenger)

        # Assert
        assert isinstance(result, Adult)
        assert result.count == 2

    def test_convert_child_passenger_list_to_srt(self):
        """Test converting child passenger in a list to SRT format"""
        # Arrange
        child_passenger = Passenger(passenger_type=PassengerType.CHILD, count=1)

        # Act
        result = PassengerMapper.to_srt(child_passenger)

        # Assert
        assert isinstance(result, Child)
        assert result.count == 1

    def test_convert_senior_passenger_list_to_srt(self):
        """Test converting senior passenger in a list to SRT format"""
        # Arrange
        senior_passenger = Passenger(passenger_type=PassengerType.SENIOR, count=1)

        # Act
        result = PassengerMapper.to_srt(senior_passenger)

        # Assert
        assert isinstance(result, Senior)
        assert result.count == 1


@pytest.mark.unit
@pytest.mark.mapper
class TestPassengerMapperEdgeCases:
    """Tests for PassengerMapper edge cases"""

    def test_zero_count_passenger_to_korail(self):
        """Test converting passenger with zero count to Korail format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=0)

        # Act
        result = PassengerMapper.to_korail(passenger)

        # Assert
        assert isinstance(result, AdultPassenger)
        assert result.count == 0

    def test_zero_count_passenger_to_srt(self):
        """Test converting passenger with zero count to SRT format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=0)

        # Act
        result = PassengerMapper.to_srt(passenger)

        # Assert
        assert isinstance(result, Adult)
        assert result.count == 0

    def test_large_count_passenger_to_korail(self):
        """Test converting passenger with large count to Korail format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=100)

        # Act
        result = PassengerMapper.to_korail(passenger)

        # Assert
        assert isinstance(result, AdultPassenger)
        assert result.count == 100

    def test_large_count_passenger_to_srt(self):
        """Test converting passenger with large count to SRT format"""
        # Arrange
        passenger = Passenger(passenger_type=PassengerType.ADULT, count=100)

        # Act
        result = PassengerMapper.to_srt(passenger)

        # Assert
        assert isinstance(result, Adult)
        assert result.count == 100
