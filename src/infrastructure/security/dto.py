"""Data Transfer Objects for security credentials"""
from dataclasses import dataclass


@dataclass
class LoginCredentials:
    """Login credentials DTO"""
    username: str
    password: str


@dataclass
class PaymentCredentials:
    """Payment credentials DTO"""
    card_number: str
    card_password: str
    expire: str
    validation_number: str  # 생년월일 또는 사업자번호
    is_corporate: bool
