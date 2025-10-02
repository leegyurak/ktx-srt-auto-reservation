"""Domain enums and constants"""

from enum import Enum


class PassengerType(Enum):
    """승객 유형"""
    ADULT = "adult"
    CHILD = "child"
    SENIOR = "senior"


class TrainType(Enum):
    """열차 유형"""
    KTX = "ktx"
    SRT = "srt"