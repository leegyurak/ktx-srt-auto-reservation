"""PyQt6 기반 KTX/SRT Macro - 개선된 버전"""
import sys
import os
import datetime
import random
import time
import threading
import platform

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QTabWidget,
    QCheckBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPalette, QColor
from domain.models.entities import ReservationRequest, Passenger, TrainSchedule, ReservationResult, CreditCard, PaymentResult
from domain.models.enums import PassengerType, TrainType
from src.infrastructure.adapters.ktx_service import KTXService
from src.infrastructure.adapters.srt_service import SRTService
from src.infrastructure.security.credential_storage import CredentialStorage
from src.constants.ui import (
    DEFAULT_KTX_DEPARTURE, DEFAULT_KTX_ARRIVAL,
    DEFAULT_SRT_DEPARTURE, DEFAULT_SRT_ARRIVAL,
    RETRY_DELAY_MIN, RETRY_DELAY_MAX,
)


def resource_path(relative_path):
    """PyInstaller로 패키징된 리소스 파일의 절대 경로를 반환합니다."""
    try:
        # PyInstaller가 생성한 임시 폴더
        base_path = sys._MEIPASS
    except AttributeError:
        # 개발 환경
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    return os.path.join(base_path, relative_path)


def setup_dark_palette(app):
    """다크 모드 팔레트 설정 (Windows 시스템 테마 무시)"""
    palette = QPalette()

    # 기본 배경/전경 색상 - Dark Theme
    palette.setColor(QPalette.ColorRole.Window, QColor(17, 24, 39))  # #111827
    palette.setColor(QPalette.ColorRole.WindowText, QColor(243, 244, 246))  # #f3f4f6
    palette.setColor(QPalette.ColorRole.Base, QColor(31, 41, 55))  # #1f2937
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(17, 24, 39))  # #111827
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(31, 41, 55))  # #1f2937
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(243, 244, 246))  # #f3f4f6
    palette.setColor(QPalette.ColorRole.Text, QColor(243, 244, 246))  # #f3f4f6
    palette.setColor(QPalette.ColorRole.Button, QColor(31, 41, 55))  # #1f2937
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(209, 213, 219))  # #d1d5db
    palette.setColor(QPalette.ColorRole.BrightText, QColor(239, 68, 68))  # #ef4444
    palette.setColor(QPalette.ColorRole.Link, QColor(96, 165, 250))  # #60a5fa
    palette.setColor(QPalette.ColorRole.Highlight, QColor(59, 130, 246))  # #3b82f6
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))  # #ffffff

    # Disabled 상태
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(75, 85, 99))  # #4b5563
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(75, 85, 99))  # #4b5563
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(75, 85, 99))  # #4b5563

    app.setPalette(palette)


STYLESHEET = """
* {
    font-family: "Pretendard Variable", -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "맑은 고딕", "Malgun Gothic", "Segoe UI", sans-serif;
}

QMainWindow {
    background: #0a0e17;
}

#centralWidget {
    background: #111827;
    border-radius: 0px;
}

/* 탭 스타일 - Dark */
QTabWidget::pane {
    border: none;
    background: transparent;
    border-radius: 16px;
}

QTabBar::tab {
    background: transparent;
    color: #6b7280;
    padding: 16px 28px;
    margin-right: 4px;
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 16px;
    font-weight: 700;
    min-width: 100px;
}

QTabBar::tab:selected {
    color: #60a5fa;
    border-bottom: 3px solid #60a5fa;
}

QTabBar::tab:hover:!selected {
    color: #93c5fd;
}

/* 헤더 */
QLabel#titleLabel {
    font-size: 28px;
    font-weight: 800;
    color: #f3f4f6;
    padding: 20px 24px;
    background: transparent;
    letter-spacing: -1px;
}

QLabel#sectionLabel {
    font-size: 16px;
    font-weight: 700;
    color: #e5e7eb;
    padding: 8px 0;
    background: transparent;
    letter-spacing: -0.5px;
}

QLabel {
    color: #9ca3af;
    font-size: 14px;
    background: transparent;
    font-weight: 500;
}

/* 카드 - Dark */
QFrame#card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(31, 41, 55, 0.8), stop:1 rgba(17, 24, 39, 0.6));
    border-radius: 16px;
    border: 1px solid rgba(75, 85, 99, 0.3);
    padding: 6px;
}

/* 입력 필드 - Dark */
QLineEdit {
    background: rgba(31, 41, 55, 0.6);
    border: 1.5px solid rgba(75, 85, 99, 0.5);
    border-radius: 12px;
    padding: 14px 16px;
    color: #f3f4f6;
    font-size: 15px;
    font-weight: 500;
    selection-background-color: #3b82f6;
}

QLineEdit:focus {
    border: 2px solid #60a5fa;
    background: rgba(31, 41, 55, 0.9);
}

QLineEdit:disabled {
    background: rgba(17, 24, 39, 0.6);
    color: #4b5563;
    border-color: rgba(55, 65, 81, 0.5);
}

QLineEdit::placeholder {
    color: #6b7280;
    font-weight: 400;
}

/* 버튼 - Dark */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #3b82f6, stop:1 #2563eb);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: 700;
    min-height: 48px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #60a5fa, stop:1 #3b82f6);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2563eb, stop:1 #1d4ed8);
}

QPushButton:disabled {
    background: rgba(55, 65, 81, 0.5);
    color: #6b7280;
}

/* Primary 버튼 */
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #8b5cf6, stop:1 #7c3aed);
    font-weight: 800;
    padding: 16px 28px;
    font-size: 16px;
    letter-spacing: -0.3px;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #a78bfa, stop:1 #8b5cf6);
}

QPushButton#primaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7c3aed, stop:1 #6d28d9);
}

QPushButton#primaryButton:disabled {
    background: rgba(55, 65, 81, 0.5);
    color: #6b7280;
}

/* Search 버튼 */
QPushButton#searchButton {
    background: rgba(55, 65, 81, 0.6);
    color: #d1d5db;
    border: none;
}

QPushButton#searchButton:hover {
    background: rgba(75, 85, 99, 0.8);
    color: #f3f4f6;
}

QPushButton#searchButton:pressed {
    background: rgba(55, 65, 81, 0.9);
}

/* Stop 버튼 */
QPushButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ef4444, stop:1 #dc2626);
    color: #ffffff;
}

QPushButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f87171, stop:1 #ef4444);
}

QPushButton#stopButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #dc2626, stop:1 #b91c1c);
}

/* Clear 버튼 */
QPushButton#clearButton {
    background: transparent;
    color: #9ca3af;
    border: 1.5px solid rgba(75, 85, 99, 0.5);
    padding: 10px 20px;
    min-height: 40px;
    font-weight: 600;
}

QPushButton#clearButton:hover {
    background: rgba(31, 41, 55, 0.5);
    color: #e5e7eb;
    border-color: rgba(107, 114, 128, 0.7);
}

QPushButton#clearButton:pressed {
    background: rgba(31, 41, 55, 0.8);
}

/* 체크박스 - Dark */
QCheckBox {
    color: #e5e7eb;
    spacing: 10px;
    font-size: 15px;
    font-weight: 600;
}

QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid #4b5563;
    background: rgba(31, 41, 55, 0.6);
}

QCheckBox::indicator:hover {
    border-color: #60a5fa;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #3b82f6, stop:1 #2563eb);
    border-color: #3b82f6;
    image: url(none);
}

/* 로그 디스플레이 - Dark */
QTextEdit#logDisplay {
    background: rgba(17, 24, 39, 0.8);
    color: #10b981;
    border: 1.5px solid rgba(75, 85, 99, 0.3);
    border-radius: 16px;
    padding: 20px;
    font-family: "SF Mono", "D2Coding", "Monaco", "Consolas", "Courier New", monospace;
    font-size: 13px;
    line-height: 1.7;
    font-weight: 500;
}

/* 스크롤바 - Dark */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(75, 85, 99, 0.6);
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(107, 114, 128, 0.8);
}

QScrollBar::handle:vertical:pressed {
    background: rgba(107, 114, 128, 1);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 4px;
}

QScrollBar::handle:horizontal {
    background: rgba(75, 85, 99, 0.6);
    border-radius: 4px;
    min-width: 40px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(107, 114, 128, 0.8);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 열차 항목 - Dark */
QFrame#trainItem {
    background: rgba(31, 41, 55, 0.5);
    border: 1.5px solid rgba(75, 85, 99, 0.3);
    border-radius: 16px;
}

QFrame#trainItem:hover {
    background: rgba(31, 41, 55, 0.8);
    border: 1.5px solid rgba(96, 165, 250, 0.5);
}

QScrollArea {
    border: none;
    background: transparent;
}
"""


class LogSignals(QObject):
    """로그 시그널"""
    log_message = pyqtSignal(str)
    show_alert_button = pyqtSignal()  # SRT 알림음 중지 버튼 표시 시그널
    show_ktx_alert_button = pyqtSignal()  # KTX 알림음 중지 버튼 표시 시그널


class TrainItemWidget(QWidget):
    """열차 항목 위젯"""
    def __init__(self, train_info: str, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 2, 0, 2)

        frame = QFrame()
        frame.setObjectName("trainItem")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        self.checkbox = QCheckBox()
        self.label = QLabel(train_info)
        self.label.setStyleSheet("font-size: 14px; color: #e4e9ed;")

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label, 1)

        self.main_layout.addWidget(frame)


class SectionCard(QFrame):
    """섹션 카드 위젯"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(12)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 타이틀
        title_label = QLabel(title)
        title_label.setObjectName("sectionLabel")
        self.main_layout.addWidget(title_label)

    def add_widget(self, widget):
        """위젯 추가"""
        self.main_layout.addWidget(widget)

    def add_layout(self, layout):
        """레이아웃 추가"""
        self.main_layout.addLayout(layout)


class TrainReservationApp(QMainWindow):
    """기차표 예약 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚄 KTX/SRT Macro")
        self.setMinimumSize(1000, 900)

        # 아이콘 설정
        icon_path = resource_path('assets/favicon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 서비스 초기화
        self.ktx_service = KTXService()
        self.srt_service = SRTService()

        # 상태 변수
        self.ktx_trains = []
        self.srt_trains = []
        self.ktx_train_widgets = []
        self.srt_train_widgets = []
        self.is_ktx_running = False
        self.is_srt_running = False
        self.is_log_visible = False
        self.is_alert_playing = False
        self.alert_thread = None

        # 로그 시그널
        self.log_signals = LogSignals()
        self.log_signals.log_message.connect(self.append_log)
        self.log_signals.show_alert_button.connect(self.show_alert_stop_button)
        self.log_signals.show_ktx_alert_button.connect(self.show_ktx_alert_stop_button)

        # UI 초기화
        self.init_ui()

        # 스타일시트 적용
        self.setStyleSheet(STYLESHEET)

        # 저장된 자격 증명 로드
        self.load_saved_credentials()

    def init_ui(self):
        """UI 초기화"""
        # 중앙 위젯
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # 외부 레이아웃 (패딩용)
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(outer_layout)

        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # 헤더
        header = QLabel("🚄 KTX/SRT Macro")
        header.setObjectName("titleLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # 탭 위젯
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self.create_ktx_tab(), "KTX 예약")
        self.tabs.addTab(self.create_srt_tab(), "SRT 예약")
        main_layout.addWidget(self.tabs)

        # 로그 토글 버튼
        self.log_toggle_btn = QPushButton("▼ 실행 로그 보기")
        self.log_toggle_btn.setObjectName("clearButton")
        self.log_toggle_btn.clicked.connect(self.toggle_log_section)
        main_layout.addWidget(self.log_toggle_btn)

        # 로그 섹션
        self.log_section = self.create_log_section()
        self.log_section.setVisible(False)
        main_layout.addWidget(self.log_section)

    def create_ktx_tab(self):
        """KTX 탭 생성"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)

        # 로그인 정보
        login_card = SectionCard("🔐 로그인 정보")
        self.ktx_id_input = QLineEdit()
        self.ktx_id_input.setPlaceholderText("아이디를 입력하세요")

        # 비밀번호 입력란 (보기/숨기기 버튼 포함)
        ktx_pw_layout = QHBoxLayout()
        ktx_pw_layout.setSpacing(8)
        self.ktx_pw_input = QLineEdit()
        self.ktx_pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.ktx_pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.ktx_pw_input.setInputMethodHints(
            Qt.InputMethodHint.ImhLatinOnly |
            Qt.InputMethodHint.ImhNoPredictiveText |
            Qt.InputMethodHint.ImhNoAutoUppercase
        )

        self.ktx_pw_toggle_btn = QPushButton("Show")
        self.ktx_pw_toggle_btn.setFixedWidth(80)
        self.ktx_pw_toggle_btn.setObjectName("clearButton")
        self.ktx_pw_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.ktx_pw_input, self.ktx_pw_toggle_btn))

        ktx_pw_layout.addWidget(self.ktx_pw_input)
        ktx_pw_layout.addWidget(self.ktx_pw_toggle_btn)

        login_card.add_widget(self.ktx_id_input)
        login_card.add_layout(ktx_pw_layout)

        # 로그인 정보 저장 체크박스
        self.ktx_save_login_check = QCheckBox("로그인 정보 저장 (안전하게 암호화됨)")
        self.ktx_save_login_check.setChecked(True)
        login_card.add_widget(self.ktx_save_login_check)

        layout.addWidget(login_card)

        # 검색 조건
        search_card = SectionCard("🔍 검색 조건")

        grid = QGridLayout()
        grid.setSpacing(10)

        self.ktx_dep_input = QLineEdit(DEFAULT_KTX_DEPARTURE)
        self.ktx_dep_input.setPlaceholderText("출발역")
        self.ktx_arr_input = QLineEdit(DEFAULT_KTX_ARRIVAL)
        self.ktx_arr_input.setPlaceholderText("도착역")

        grid.addWidget(QLabel("출발역"), 0, 0)
        grid.addWidget(self.ktx_dep_input, 0, 1)
        grid.addWidget(QLabel("도착역"), 0, 2)
        grid.addWidget(self.ktx_arr_input, 0, 3)

        self.ktx_date_input = QLineEdit(datetime.datetime.now().strftime("%Y%m%d"))
        self.ktx_date_input.setPlaceholderText("YYYYMMDD")
        self.ktx_time_input = QLineEdit(
            datetime.datetime.now().strftime("%H%M")
        )
        self.ktx_time_input.setPlaceholderText("HHMM")

        grid.addWidget(QLabel("출발일"), 1, 0)
        grid.addWidget(self.ktx_date_input, 1, 1)
        grid.addWidget(QLabel("출발시간"), 1, 2)
        grid.addWidget(self.ktx_time_input, 1, 3)

        search_card.add_layout(grid)

        # 승객 수 - 한 줄에 3개
        passenger_layout = QHBoxLayout()
        passenger_layout.setSpacing(12)

        self.ktx_adult_input = QLineEdit("1")
        self.ktx_adult_input.setPlaceholderText("어른")
        self.ktx_child_input = QLineEdit("0")
        self.ktx_child_input.setPlaceholderText("어린이")
        self.ktx_senior_input = QLineEdit("0")
        self.ktx_senior_input.setPlaceholderText("경로")

        adult_layout = QVBoxLayout()
        adult_layout.setSpacing(4)
        adult_layout.addWidget(QLabel("어른"))
        adult_layout.addWidget(self.ktx_adult_input)

        child_layout = QVBoxLayout()
        child_layout.setSpacing(4)
        child_layout.addWidget(QLabel("어린이"))
        child_layout.addWidget(self.ktx_child_input)

        senior_layout = QVBoxLayout()
        senior_layout.setSpacing(4)
        senior_layout.addWidget(QLabel("경로"))
        senior_layout.addWidget(self.ktx_senior_input)

        passenger_layout.addLayout(adult_layout)
        passenger_layout.addLayout(child_layout)
        passenger_layout.addLayout(senior_layout)

        search_card.add_layout(passenger_layout)

        # 특실 옵션
        self.ktx_special_seat_check = QCheckBox("특실 우선 예약")
        search_card.add_widget(self.ktx_special_seat_check)

        self.ktx_only_special_seat_check = QCheckBox("특실만 탐색")
        search_card.add_widget(self.ktx_only_special_seat_check)

        # 두 체크박스가 동시에 체크되지 않도록 설정
        def on_ktx_special_seat_changed(state):
            if state and self.ktx_only_special_seat_check.isChecked():
                self.ktx_only_special_seat_check.setChecked(False)

        def on_ktx_only_special_seat_changed(state):
            if state and self.ktx_special_seat_check.isChecked():
                self.ktx_special_seat_check.setChecked(False)

        self.ktx_special_seat_check.stateChanged.connect(on_ktx_special_seat_changed)
        self.ktx_only_special_seat_check.stateChanged.connect(on_ktx_only_special_seat_changed)

        self.ktx_search_btn = QPushButton("🔍 열차 검색")
        self.ktx_search_btn.setObjectName("searchButton")
        self.ktx_search_btn.clicked.connect(self.search_ktx)
        search_card.add_widget(self.ktx_search_btn)

        layout.addWidget(search_card)

        # 열차 선택
        self.ktx_trains_card = SectionCard("🚄 열차 선택")
        self.ktx_trains_layout = QVBoxLayout()
        self.ktx_trains_card.add_layout(self.ktx_trains_layout)
        self.ktx_trains_card.setVisible(False)
        layout.addWidget(self.ktx_trains_card)

        # 결제 정보
        self.ktx_payment_card = SectionCard("💳 결제 정보")

        self.ktx_payment_card_num_input = QLineEdit()
        self.ktx_payment_card_num_input.setPlaceholderText("카드번호 (16자리)")
        self.ktx_payment_card_pw_input = QLineEdit()
        self.ktx_payment_card_pw_input.setPlaceholderText("카드 비밀번호 앞 2자리")
        self.ktx_payment_card_pw_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.ktx_payment_card.add_widget(self.ktx_payment_card_num_input)
        self.ktx_payment_card.add_widget(self.ktx_payment_card_pw_input)

        self.ktx_payment_corporate_check = QCheckBox("법인카드 사용")
        self.ktx_payment_card.add_widget(self.ktx_payment_corporate_check)

        self.ktx_payment_birth_input = QLineEdit()
        self.ktx_payment_birth_input.setPlaceholderText("생년월일 (YYMMDD)")
        self.ktx_payment_business_num_input = QLineEdit()
        self.ktx_payment_business_num_input.setPlaceholderText("사업자번호 (10자리)")
        self.ktx_payment_business_num_input.setVisible(False)
        self.ktx_payment_expire_input = QLineEdit()
        self.ktx_payment_expire_input.setPlaceholderText("유효기간 (YYMM)")

        def toggle_ktx_corporate():
            if self.ktx_payment_corporate_check.isChecked():
                self.ktx_payment_birth_input.setVisible(False)
                self.ktx_payment_business_num_input.setVisible(True)
            else:
                self.ktx_payment_birth_input.setVisible(True)
                self.ktx_payment_business_num_input.setVisible(False)

        self.ktx_payment_corporate_check.stateChanged.connect(toggle_ktx_corporate)

        self.ktx_payment_card.add_widget(self.ktx_payment_birth_input)
        self.ktx_payment_card.add_widget(self.ktx_payment_business_num_input)
        self.ktx_payment_card.add_widget(self.ktx_payment_expire_input)

        # 결제 정보 저장 체크박스
        self.ktx_save_payment_check = QCheckBox("결제 정보 저장 (안전하게 암호화됨)")
        self.ktx_save_payment_check.setChecked(True)
        self.ktx_payment_card.add_widget(self.ktx_save_payment_check)

        self.ktx_payment_card.setVisible(False)
        layout.addWidget(self.ktx_payment_card)

        # 예약 버튼
        self.ktx_action_widget = QWidget()
        action_layout = QHBoxLayout(self.ktx_action_widget)
        action_layout.setSpacing(12)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.ktx_start_btn = QPushButton("🚀 예약 시작")
        self.ktx_start_btn.setObjectName("primaryButton")
        self.ktx_start_btn.setEnabled(False)
        self.ktx_start_btn.clicked.connect(self.start_ktx)

        self.ktx_stop_btn = QPushButton("⏹ 예약 중지")
        self.ktx_stop_btn.setObjectName("stopButton")
        self.ktx_stop_btn.setEnabled(False)
        self.ktx_stop_btn.clicked.connect(self.stop_ktx)

        self.ktx_alert_stop_btn = QPushButton("🔇 알림음 중지")
        self.ktx_alert_stop_btn.setObjectName("stopButton")
        self.ktx_alert_stop_btn.setVisible(False)
        self.ktx_alert_stop_btn.clicked.connect(self.stop_ktx_alert)

        action_layout.addWidget(self.ktx_start_btn)
        action_layout.addWidget(self.ktx_stop_btn)
        action_layout.addWidget(self.ktx_alert_stop_btn)

        self.ktx_action_widget.setVisible(False)
        layout.addWidget(self.ktx_action_widget)

        layout.addStretch()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        return widget

    def create_srt_tab(self):
        """SRT 탭 생성"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(10, 10, 10, 10)

        # 로그인 정보
        login_card = SectionCard("🔐 로그인 정보")
        self.srt_id_input = QLineEdit()
        self.srt_id_input.setPlaceholderText("아이디를 입력하세요")

        # 비밀번호 입력란 (보기/숨기기 버튼 포함)
        srt_pw_layout = QHBoxLayout()
        srt_pw_layout.setSpacing(8)
        self.srt_pw_input = QLineEdit()
        self.srt_pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.srt_pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.srt_pw_input.setInputMethodHints(
            Qt.InputMethodHint.ImhLatinOnly |
            Qt.InputMethodHint.ImhNoPredictiveText |
            Qt.InputMethodHint.ImhNoAutoUppercase
        )

        self.srt_pw_toggle_btn = QPushButton("Show")
        self.srt_pw_toggle_btn.setFixedWidth(80)
        self.srt_pw_toggle_btn.setObjectName("clearButton")
        self.srt_pw_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.srt_pw_input, self.srt_pw_toggle_btn))

        srt_pw_layout.addWidget(self.srt_pw_input)
        srt_pw_layout.addWidget(self.srt_pw_toggle_btn)

        login_card.add_widget(self.srt_id_input)
        login_card.add_layout(srt_pw_layout)

        # 로그인 정보 저장 체크박스
        self.srt_save_login_check = QCheckBox("로그인 정보 저장 (안전하게 암호화됨)")
        self.srt_save_login_check.setChecked(True)
        login_card.add_widget(self.srt_save_login_check)

        layout.addWidget(login_card)

        # 검색 조건
        search_card = SectionCard("🔍 검색 조건")

        grid = QGridLayout()
        grid.setSpacing(10)

        self.srt_dep_input = QLineEdit(DEFAULT_SRT_DEPARTURE)
        self.srt_dep_input.setPlaceholderText("출발역")
        self.srt_arr_input = QLineEdit(DEFAULT_SRT_ARRIVAL)
        self.srt_arr_input.setPlaceholderText("도착역")

        grid.addWidget(QLabel("출발역"), 0, 0)
        grid.addWidget(self.srt_dep_input, 0, 1)
        grid.addWidget(QLabel("도착역"), 0, 2)
        grid.addWidget(self.srt_arr_input, 0, 3)

        self.srt_date_input = QLineEdit(datetime.datetime.now().strftime("%Y%m%d"))
        self.srt_date_input.setPlaceholderText("YYYYMMDD")
        self.srt_time_input = QLineEdit(
            datetime.datetime.now().strftime("%H%M")
        )
        self.srt_time_input.setPlaceholderText("HHMM")

        grid.addWidget(QLabel("출발일"), 1, 0)
        grid.addWidget(self.srt_date_input, 1, 1)
        grid.addWidget(QLabel("출발시간"), 1, 2)
        grid.addWidget(self.srt_time_input, 1, 3)

        search_card.add_layout(grid)

        # 승객 수 - 한 줄에 3개
        passenger_layout = QHBoxLayout()
        passenger_layout.setSpacing(12)

        self.srt_adult_input = QLineEdit("1")
        self.srt_adult_input.setPlaceholderText("어른")
        self.srt_child_input = QLineEdit("0")
        self.srt_child_input.setPlaceholderText("어린이")
        self.srt_senior_input = QLineEdit("0")
        self.srt_senior_input.setPlaceholderText("경로")

        adult_layout = QVBoxLayout()
        adult_layout.setSpacing(4)
        adult_layout.addWidget(QLabel("어른"))
        adult_layout.addWidget(self.srt_adult_input)

        child_layout = QVBoxLayout()
        child_layout.setSpacing(4)
        child_layout.addWidget(QLabel("어린이"))
        child_layout.addWidget(self.srt_child_input)

        senior_layout = QVBoxLayout()
        senior_layout.setSpacing(4)
        senior_layout.addWidget(QLabel("경로"))
        senior_layout.addWidget(self.srt_senior_input)

        passenger_layout.addLayout(adult_layout)
        passenger_layout.addLayout(child_layout)
        passenger_layout.addLayout(senior_layout)

        search_card.add_layout(passenger_layout)

        # 특실 옵션
        self.srt_special_seat_check = QCheckBox("특실 우선 예약")
        search_card.add_widget(self.srt_special_seat_check)

        self.srt_only_special_seat_check = QCheckBox("특실만 탐색")
        search_card.add_widget(self.srt_only_special_seat_check)

        # 두 체크박스가 동시에 체크되지 않도록 설정
        def on_srt_special_seat_changed(state):
            if state and self.srt_only_special_seat_check.isChecked():
                self.srt_only_special_seat_check.setChecked(False)

        def on_srt_only_special_seat_changed(state):
            if state and self.srt_special_seat_check.isChecked():
                self.srt_special_seat_check.setChecked(False)

        self.srt_special_seat_check.stateChanged.connect(on_srt_special_seat_changed)
        self.srt_only_special_seat_check.stateChanged.connect(on_srt_only_special_seat_changed)

        self.srt_search_btn = QPushButton("🔍 열차 검색")
        self.srt_search_btn.setObjectName("searchButton")
        self.srt_search_btn.clicked.connect(self.search_srt)
        search_card.add_widget(self.srt_search_btn)

        layout.addWidget(search_card)

        # 열차 선택
        self.srt_trains_card = SectionCard("🚄 열차 선택")
        self.srt_trains_layout = QVBoxLayout()
        self.srt_trains_card.add_layout(self.srt_trains_layout)
        self.srt_trains_card.setVisible(False)
        layout.addWidget(self.srt_trains_card)

        # 결제 정보
        self.srt_payment_card = SectionCard("💳 결제 정보")

        self.srt_payment_card_num_input = QLineEdit()
        self.srt_payment_card_num_input.setPlaceholderText("카드번호 (16자리)")
        self.srt_payment_card_pw_input = QLineEdit()
        self.srt_payment_card_pw_input.setPlaceholderText("카드 비밀번호 앞 2자리")
        self.srt_payment_card_pw_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.srt_payment_card.add_widget(self.srt_payment_card_num_input)
        self.srt_payment_card.add_widget(self.srt_payment_card_pw_input)

        self.srt_payment_corporate_check = QCheckBox("법인카드 사용")
        self.srt_payment_card.add_widget(self.srt_payment_corporate_check)

        self.srt_payment_birth_input = QLineEdit()
        self.srt_payment_birth_input.setPlaceholderText("생년월일 (YYMMDD)")
        self.srt_payment_business_num_input = QLineEdit()
        self.srt_payment_business_num_input.setPlaceholderText("사업자번호 (10자리)")
        self.srt_payment_business_num_input.setVisible(False)
        self.srt_payment_expire_input = QLineEdit()
        self.srt_payment_expire_input.setPlaceholderText("유효기간 (YYMM)")

        def toggle_srt_corporate():
            if self.srt_payment_corporate_check.isChecked():
                self.srt_payment_birth_input.setVisible(False)
                self.srt_payment_business_num_input.setVisible(True)
            else:
                self.srt_payment_birth_input.setVisible(True)
                self.srt_payment_business_num_input.setVisible(False)

        self.srt_payment_corporate_check.stateChanged.connect(toggle_srt_corporate)

        self.srt_payment_card.add_widget(self.srt_payment_birth_input)
        self.srt_payment_card.add_widget(self.srt_payment_business_num_input)
        self.srt_payment_card.add_widget(self.srt_payment_expire_input)

        # 결제 정보 저장 체크박스
        self.srt_save_payment_check = QCheckBox("결제 정보 저장 (안전하게 암호화됨)")
        self.srt_save_payment_check.setChecked(True)
        self.srt_payment_card.add_widget(self.srt_save_payment_check)

        self.srt_payment_card.setVisible(False)
        layout.addWidget(self.srt_payment_card)

        # 예약 버튼
        self.srt_action_widget = QWidget()
        action_layout = QHBoxLayout(self.srt_action_widget)
        action_layout.setSpacing(12)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.srt_start_btn = QPushButton("🚀 예약 시작")
        self.srt_start_btn.setObjectName("primaryButton")
        self.srt_start_btn.setEnabled(False)
        self.srt_start_btn.clicked.connect(self.start_srt)

        self.srt_stop_btn = QPushButton("⏹ 예약 중지")
        self.srt_stop_btn.setObjectName("stopButton")
        self.srt_stop_btn.setEnabled(False)
        self.srt_stop_btn.clicked.connect(self.stop_srt)

        self.srt_alert_stop_btn = QPushButton("🔇 알림음 중지")
        self.srt_alert_stop_btn.setObjectName("stopButton")
        self.srt_alert_stop_btn.setVisible(False)
        self.srt_alert_stop_btn.clicked.connect(self.stop_alert)

        action_layout.addWidget(self.srt_start_btn)
        action_layout.addWidget(self.srt_stop_btn)
        action_layout.addWidget(self.srt_alert_stop_btn)

        self.srt_action_widget.setVisible(False)
        layout.addWidget(self.srt_action_widget)

        layout.addStretch()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        return widget

    def create_log_section(self):
        """로그 섹션 생성"""
        # 카드 프레임
        card = QFrame()
        card.setObjectName("card")

        main_layout = QVBoxLayout(card)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 헤더 (제목 + 지우기 버튼)
        header_layout = QHBoxLayout()
        title_label = QLabel("📋 실행 로그")
        title_label.setObjectName("sectionLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        clear_btn = QPushButton("🗑️ 지우기")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(clear_btn)

        main_layout.addLayout(header_layout)

        # 로그 디스플레이
        self.log_display = QTextEdit()
        self.log_display.setObjectName("logDisplay")
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(200)
        self.log_display.setMaximumHeight(250)
        main_layout.addWidget(self.log_display)

        return card

    def add_log(self, message: str):
        """로그 추가 (스레드 안전)"""
        self.log_signals.log_message.emit(message)

    def append_log(self, message: str):
        """로그 표시"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_display.append(f"[{timestamp}] {message}")
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """로그 지우기"""
        self.log_display.clear()

    def load_saved_credentials(self):
        """저장된 자격 증명 로드"""
        # KTX 로그인 정보 로드
        ktx_login = CredentialStorage.load_ktx_login()
        if ktx_login:
            self.ktx_id_input.setText(ktx_login.username)
            self.ktx_pw_input.setText(ktx_login.password)
            self.ktx_save_login_check.setChecked(True)

        # SRT 로그인 정보 로드
        srt_login = CredentialStorage.load_srt_login()
        if srt_login:
            self.srt_id_input.setText(srt_login.username)
            self.srt_pw_input.setText(srt_login.password)
            self.srt_save_login_check.setChecked(True)

        # 결제 정보 로드 (KTX/SRT 공통)
        payment = CredentialStorage.load_payment()
        if payment:
            # KTX 결제 정보 입력
            self.ktx_payment_card_num_input.setText(payment.card_number)
            self.ktx_payment_card_pw_input.setText(payment.card_password)
            self.ktx_payment_expire_input.setText(payment.expire)
            self.ktx_payment_corporate_check.setChecked(payment.is_corporate)
            if payment.is_corporate:
                self.ktx_payment_business_num_input.setText(payment.validation_number)
            else:
                self.ktx_payment_birth_input.setText(payment.validation_number)
            self.ktx_save_payment_check.setChecked(True)

            # SRT 결제 정보 입력 (동일한 정보)
            self.srt_payment_card_num_input.setText(payment.card_number)
            self.srt_payment_card_pw_input.setText(payment.card_password)
            self.srt_payment_expire_input.setText(payment.expire)
            self.srt_payment_corporate_check.setChecked(payment.is_corporate)
            if payment.is_corporate:
                self.srt_payment_business_num_input.setText(payment.validation_number)
            else:
                self.srt_payment_birth_input.setText(payment.validation_number)
            self.srt_save_payment_check.setChecked(True)

    def toggle_password_visibility(self, password_input: QLineEdit, toggle_btn: QPushButton):
        """비밀번호 보기/숨기기 토글"""
        if password_input.echoMode() == QLineEdit.EchoMode.Password:
            password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_btn.setText("Hide")
        else:
            password_input.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_btn.setText("Show")

    def toggle_log_section(self):
        """로그 섹션 보기/숨기기 토글"""
        self.is_log_visible = not self.is_log_visible
        self.log_section.setVisible(self.is_log_visible)
        if self.is_log_visible:
            self.log_toggle_btn.setText("▲ 실행 로그 숨기기")
        else:
            self.log_toggle_btn.setText("▼ 실행 로그 보기")

    def search_ktx(self):
        """KTX 열차 검색"""
        threading.Thread(target=self._search_ktx_thread, daemon=True).start()

    def _search_ktx_thread(self):
        """KTX 검색 스레드"""
        # 로그인 정보 검증
        if not self.ktx_id_input.text().strip() or not self.ktx_pw_input.text().strip():
            self.add_log("✗ 입력 오류: 아이디와 비밀번호를 입력해주세요")
            return

        self.ktx_search_btn.setEnabled(False)
        self.add_log("🔐 KTX 로그인 중...")

        try:
            username = self.ktx_id_input.text()
            password = self.ktx_pw_input.text()
            login_result = self.ktx_service.login(username, password)

            if not login_result:
                self.add_log("✗ 로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다")
                self.ktx_search_btn.setEnabled(True)
                return

            self.add_log("✓ 로그인 성공")

            # 로그인 정보 저장 (체크박스 확인)
            if self.ktx_save_login_check.isChecked():
                CredentialStorage.save_ktx_login(username, password)
            else:
                CredentialStorage.delete_ktx_login()
            self.add_log("🔍 열차 검색 중...")

            departure_date = datetime.datetime.strptime(self.ktx_date_input.text(), "%Y%m%d").date()
            departure_time = self.ktx_time_input.text() + "00"

            # 승객 정보 수집
            passengers = []
            adult_count = int(self.ktx_adult_input.text() or "0")
            child_count = int(self.ktx_child_input.text() or "0")
            senior_count = int(self.ktx_senior_input.text() or "0")

            if adult_count > 0:
                passengers.append(Passenger(PassengerType.ADULT, adult_count))
            if child_count > 0:
                passengers.append(Passenger(PassengerType.CHILD, child_count))
            if senior_count > 0:
                passengers.append(Passenger(PassengerType.SENIOR, senior_count))

            if not passengers:
                self.add_log("✗ 최소 1명 이상의 승객이 필요합니다")
                self.ktx_search_btn.setEnabled(True)
                return

            request = ReservationRequest(
                departure_station=self.ktx_dep_input.text(),
                arrival_station=self.ktx_arr_input.text(),
                departure_date=departure_date,
                departure_time=departure_time,
                passengers=passengers,
                train_type=TrainType.KTX,
                is_special_seat_allowed=self.ktx_special_seat_check.isChecked(),
                is_only_special_seat=self.ktx_only_special_seat_check.isChecked()
            )

            trains = self.ktx_service.search_trains(request)
            self.ktx_trains = trains

            if trains:
                self.add_log(f"✓ {len(trains)}개의 열차를 찾았습니다")
                QTimer.singleShot(0, self.display_ktx_trains)
            else:
                self.add_log("✗ 열차를 찾을 수 없습니다")

        except Exception as e:
            self.add_log(f"✗ 로그인 중 오류가 발생했습니다: {str(e)}")

        finally:
            self.ktx_search_btn.setEnabled(True)

    def display_ktx_trains(self):
        """KTX 열차 목록 표시"""
        # 기존 위젯 제거
        while self.ktx_trains_layout.count():
            item = self.ktx_trains_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.ktx_train_widgets = []

        for train in self.ktx_trains:
            train_info = f"{train.train_number} | 🚉 {train.departure_time.strftime('%H:%M')} → {train.arrival_time.strftime('%H:%M')}"
            widget = TrainItemWidget(train_info)
            widget.checkbox.stateChanged.connect(self.update_ktx_start_button)
            self.ktx_train_widgets.append(widget)
            self.ktx_trains_layout.addWidget(widget)

        # 결제 정보 로드 (이미 저장된 정보가 있다면 다시 불러오기)
        payment = CredentialStorage.load_payment()
        if payment:
            self.ktx_payment_card_num_input.setText(payment.card_number)
            self.ktx_payment_card_pw_input.setText(payment.card_password)
            self.ktx_payment_expire_input.setText(payment.expire)
            self.ktx_payment_corporate_check.setChecked(payment.is_corporate)
            if payment.is_corporate:
                self.ktx_payment_business_num_input.setText(payment.validation_number)
            else:
                self.ktx_payment_birth_input.setText(payment.validation_number)
            self.ktx_save_payment_check.setChecked(True)

        self.ktx_trains_card.setVisible(True)
        self.ktx_payment_card.setVisible(True)
        self.ktx_action_widget.setVisible(True)
        self.update_ktx_start_button()

    def update_ktx_start_button(self):
        """KTX 시작 버튼 활성화 상태 업데이트"""
        has_selection = any(w.checkbox.isChecked() for w in self.ktx_train_widgets)
        self.ktx_start_btn.setEnabled(has_selection)

    def start_ktx(self):
        """KTX 예약 시작"""
        selected_indices = [i for i, w in enumerate(self.ktx_train_widgets) if w.checkbox.isChecked()]

        if not selected_indices:
            self.add_log("✗ 열차를 선택해주세요")
            return

        # 결제 정보 미리 저장 (체크박스가 체크되어 있고 정보가 유효한 경우)
        if self.ktx_save_payment_check.isChecked() and self._validate_ktx_payment_info():
            try:
                card_number = self.ktx_payment_card_num_input.text()
                card_pw = self.ktx_payment_card_pw_input.text()
                is_corporate = self.ktx_payment_corporate_check.isChecked()
                validation_number = (
                    self.ktx_payment_birth_input.text()
                    if not is_corporate
                    else self.ktx_payment_business_num_input.text()
                )
                expire = self.ktx_payment_expire_input.text()

                CredentialStorage.save_payment(
                    card_number=card_number,
                    card_password=card_pw,
                    expire=expire,
                    validation_number=validation_number,
                    is_corporate=is_corporate
                )
            except Exception:
                pass  # 저장 실패 시 조용히 무시

        self.is_ktx_running = True
        self.ktx_start_btn.setEnabled(False)
        self.ktx_stop_btn.setEnabled(True)

        self.add_log("🚀 KTX 예약을 시작합니다")

        threading.Thread(
            target=self._ktx_reservation_loop,
            args=(selected_indices,),
            daemon=True
        ).start()

    def _ktx_reservation_loop(self, selected_indices):
        """KTX 예약 루프"""
        selected_trains = [self.ktx_trains[i] for i in selected_indices]
        attempt = 0

        # 승객 정보 수집
        passengers = []
        adult_count = int(self.ktx_adult_input.text() or "0")
        child_count = int(self.ktx_child_input.text() or "0")
        senior_count = int(self.ktx_senior_input.text() or "0")

        if adult_count > 0:
            passengers.append(Passenger(PassengerType.ADULT, adult_count))
        if child_count > 0:
            passengers.append(Passenger(PassengerType.CHILD, child_count))
        if senior_count > 0:
            passengers.append(Passenger(PassengerType.SENIOR, senior_count))

        while self.is_ktx_running:
            attempt += 1
            self.add_log(f"🔄 예약 시도 #{attempt}")

            # 500번마다 세션 초기화
            if attempt % 500 == 0:
                self.add_log("🔄 세션 초기화 중...")
                try:
                    username = self.ktx_id_input.text()
                    password = self.ktx_pw_input.text()
                    self.ktx_service.clear()
                    self.add_log("✓ 세션 초기화 완료")
                    self.add_log("🔐 재로그인 중...")
                    login_result = self.ktx_service.login(username, password)
                    if login_result:
                        self.add_log("✓ 재로그인 성공")
                    else:
                        self.add_log("✗ 재로그인 실패")
                        self.is_ktx_running = False
                        return
                except Exception as e:
                    self.add_log(f"✗ 세션 초기화 중 오류: {str(e)}")
                    self.is_ktx_running = False
                    return

            try:
                # 선택한 모든 열차를 한 번에 시도
                train_numbers = ", ".join([t.train_number for t in selected_trains])
                self.add_log(f"  → 열차 예약 시도 중: {train_numbers}")

                request = ReservationRequest(
                    departure_station=selected_trains[0].departure_station,
                    arrival_station=selected_trains[0].arrival_station,
                    departure_date=selected_trains[0].departure_time.date(),
                    departure_time=selected_trains[0].departure_time.strftime("%H%M%S"),
                    passengers=passengers,
                    train_type=TrainType.KTX,
                    is_special_seat_allowed=self.ktx_special_seat_check.isChecked(),
                    is_only_special_seat=self.ktx_only_special_seat_check.isChecked()
                )
                reservation = self.ktx_service.reserve_train(selected_trains, request)
                if reservation.success:
                    self.add_log(f"  ✓ 예약 성공! (열차: {reservation.train_schedule.train_number})")
                    self.add_log(f"  예약번호: {reservation.reservation_number}")

                    # 결제 정보 검증
                    if not self._validate_ktx_payment_info():
                        self.add_log("  ✗ 예약은 완료되었으나 결제 정보가 입력되지 않았습니다.")
                        self.add_log(f"    예약번호: {reservation.reservation_number}")
                        self.add_log("    알림음 중지 버튼을 눌러 알림음을 중지하고")
                        self.add_log("    앱에 들어가 10분 내에 결제해주세요.")
                        self.is_ktx_running = False  # 예약 루프 중지
                        # 반복 알림음 재생 시작
                        self.alert_thread = threading.Thread(target=self._play_alert_sound_loop, daemon=True)
                        self.alert_thread.start()
                        # 시그널로 알림음 중지 버튼 표시
                        self.log_signals.show_ktx_alert_button.emit()
                        return  # 예약 루프 종료

                    # 결제 진행
                    payment = self._process_ktx_payment(reservation)

                    if payment.success:
                        self.add_log(f"  ✓ 결제 완료!")
                        self.is_ktx_running = False
                        # 버튼 상태 업데이트
                        QTimer.singleShot(0, lambda: self.ktx_start_btn.setEnabled(True))
                        QTimer.singleShot(0, lambda: self.ktx_stop_btn.setEnabled(False))
                        return  # 예약 루프 종료
                    else:
                        self.add_log("  ✗ 예약은 완료되었으나 결제에 실패했습니다.")
                        self.add_log(f"    예약번호: {payment.reservation_number}")
                        self.add_log("    알림음 중지 버튼을 눌러 알림음을 중지하고")
                        self.add_log("    앱에 들어가 10분 내에 결제해주세요.")
                        self.is_ktx_running = False  # 예약 루프 중지
                        # 반복 알림음 재생 시작
                        self.alert_thread = threading.Thread(target=self._play_alert_sound_loop, daemon=True)
                        self.alert_thread.start()
                        # 시그널로 알림음 중지 버튼 표시
                        self.log_signals.show_ktx_alert_button.emit()
                        return  # 예약 루프 종료
                else:
                    self.add_log(f"  ✗ 예약 실패: {reservation.message}")
                    delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                    self.add_log(f"⏳ {delay:.1f}초 후 재시도...")
                    time.sleep(delay)

            except Exception as e:
                self.add_log(f"  ✗ 오류: {str(e)}")
                delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                time.sleep(delay)

    def stop_ktx(self):
        """KTX 예약 중지"""
        self.is_ktx_running = False
        self.is_alert_playing = False  # 알림음 중지
        self.add_log("⏹ KTX 예약을 중지했습니다")
        self.ktx_start_btn.setEnabled(True)
        self.ktx_stop_btn.setEnabled(False)

    def search_srt(self):
        """SRT 열차 검색"""
        threading.Thread(target=self._search_srt_thread, daemon=True).start()

    def _search_srt_thread(self):
        """SRT 검색 스레드"""
        # 로그인 정보 검증
        if not self.srt_id_input.text().strip() or not self.srt_pw_input.text().strip():
            self.add_log("✗ 입력 오류: 아이디와 비밀번호를 입력해주세요")
            return

        self.srt_search_btn.setEnabled(False)
        self.add_log("🔐 SRT 로그인 중...")

        try:
            username = self.srt_id_input.text()
            password = self.srt_pw_input.text()
            login_result = self.srt_service.login(username, password)

            if not login_result:
                self.add_log("✗ 로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다")
                self.srt_search_btn.setEnabled(True)
                return

            self.add_log("✓ 로그인 성공")

            # 로그인 정보 저장 (체크박스 확인)
            if self.srt_save_login_check.isChecked():
                CredentialStorage.save_srt_login(username, password)
            else:
                CredentialStorage.delete_srt_login()
            self.add_log("🔍 열차 검색 중...")

            departure_date = datetime.datetime.strptime(self.srt_date_input.text(), "%Y%m%d").date()
            departure_time = self.srt_time_input.text() + "00"

            # 승객 정보 수집
            passengers = []
            adult_count = int(self.srt_adult_input.text() or "0")
            child_count = int(self.srt_child_input.text() or "0")
            senior_count = int(self.srt_senior_input.text() or "0")

            if adult_count > 0:
                passengers.append(Passenger(PassengerType.ADULT, adult_count))
            if child_count > 0:
                passengers.append(Passenger(PassengerType.CHILD, child_count))
            if senior_count > 0:
                passengers.append(Passenger(PassengerType.SENIOR, senior_count))

            if not passengers:
                self.add_log("✗ 최소 1명 이상의 승객이 필요합니다")
                self.srt_search_btn.setEnabled(True)
                return

            request = ReservationRequest(
                departure_station=self.srt_dep_input.text(),
                arrival_station=self.srt_arr_input.text(),
                departure_date=departure_date,
                departure_time=departure_time,
                passengers=passengers,
                train_type=TrainType.SRT,
                is_special_seat_allowed=self.srt_special_seat_check.isChecked(),
                is_only_special_seat=self.srt_only_special_seat_check.isChecked()
            )

            trains = self.srt_service.search_trains(request)
            self.srt_trains = trains

            if trains:
                self.add_log(f"✓ {len(trains)}개의 열차를 찾았습니다")
                QTimer.singleShot(0, self.display_srt_trains)
            else:
                self.add_log("✗ 열차를 찾을 수 없습니다")

        except Exception as e:
            self.add_log(f"✗ 로그인 중 오류가 발생했습니다: {str(e)}")

        finally:
            self.srt_search_btn.setEnabled(True)

    def display_srt_trains(self):
        """SRT 열차 목록 표시"""
        # 기존 위젯 제거
        while self.srt_trains_layout.count():
            item = self.srt_trains_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.srt_train_widgets = []

        for train in self.srt_trains:
            train_info = f"{train.train_number} | 🚉 {train.departure_time.strftime('%H:%M')} → {train.arrival_time.strftime('%H:%M')}"
            widget = TrainItemWidget(train_info)
            widget.checkbox.stateChanged.connect(self.update_srt_start_button)
            self.srt_train_widgets.append(widget)
            self.srt_trains_layout.addWidget(widget)

        # 결제 정보 로드 (이미 저장된 정보가 있다면 다시 불러오기)
        payment = CredentialStorage.load_payment()
        if payment:
            self.srt_payment_card_num_input.setText(payment.card_number)
            self.srt_payment_card_pw_input.setText(payment.card_password)
            self.srt_payment_expire_input.setText(payment.expire)
            self.srt_payment_corporate_check.setChecked(payment.is_corporate)
            if payment.is_corporate:
                self.srt_payment_business_num_input.setText(payment.validation_number)
            else:
                self.srt_payment_birth_input.setText(payment.validation_number)
            self.srt_save_payment_check.setChecked(True)

        self.srt_trains_card.setVisible(True)
        self.srt_payment_card.setVisible(True)
        self.srt_action_widget.setVisible(True)
        self.update_srt_start_button()

    def update_srt_start_button(self):
        """SRT 시작 버튼 활성화 상태 업데이트"""
        has_selection = any(w.checkbox.isChecked() for w in self.srt_train_widgets)
        self.srt_start_btn.setEnabled(has_selection)

    def start_srt(self):
        """SRT 예약 시작"""
        selected_indices = [i for i, w in enumerate(self.srt_train_widgets) if w.checkbox.isChecked()]

        if not selected_indices:
            self.add_log("✗ 열차를 선택해주세요")
            return

        # 결제 정보 미리 저장 (체크박스가 체크되어 있고 정보가 유효한 경우)
        if self.srt_save_payment_check.isChecked() and self._validate_srt_payment_info():
            try:
                card_number = self.srt_payment_card_num_input.text()
                card_pw = self.srt_payment_card_pw_input.text()
                is_corporate = self.srt_payment_corporate_check.isChecked()
                validation_number = (
                    self.srt_payment_birth_input.text()
                    if not is_corporate
                    else self.srt_payment_business_num_input.text()
                )
                expire = self.srt_payment_expire_input.text()

                CredentialStorage.save_payment(
                    card_number=card_number,
                    card_password=card_pw,
                    expire=expire,
                    validation_number=validation_number,
                    is_corporate=is_corporate
                )
            except Exception:
                pass  # 저장 실패 시 조용히 무시

        self.is_srt_running = True
        self.srt_start_btn.setEnabled(False)
        self.srt_stop_btn.setEnabled(True)

        self.add_log("🚀 SRT 예약을 시작합니다")

        threading.Thread(
            target=self._srt_reservation_loop,
            args=(selected_indices,),
            daemon=True,
        ).start()

    def _srt_reservation_loop(self, selected_indices):
        """SRT 예약 루프"""
        selected_trains: list[TrainSchedule] = [self.srt_trains[i] for i in selected_indices]
        attempt = 0

        # 승객 정보 수집
        passengers = []
        adult_count = int(self.srt_adult_input.text() or "0")
        child_count = int(self.srt_child_input.text() or "0")
        senior_count = int(self.srt_senior_input.text() or "0")

        if adult_count > 0:
            passengers.append(Passenger(PassengerType.ADULT, adult_count))
        if child_count > 0:
            passengers.append(Passenger(PassengerType.CHILD, child_count))
        if senior_count > 0:
            passengers.append(Passenger(PassengerType.SENIOR, senior_count))

        while self.is_srt_running:
            attempt += 1
            self.add_log(f"🔄 예약 시도 #{attempt}")

            # 500번마다 세션 초기화
            if attempt % 500 == 0:
                self.add_log("🔄 세션 초기화 중...")
                try:
                    username = self.srt_id_input.text()
                    password = self.srt_pw_input.text()
                    self.srt_service.clear()
                    self.add_log("✓ 세션 초기화 완료")
                    self.add_log("🔐 재로그인 중...")
                    login_result = self.srt_service.login(username, password)
                    if login_result:
                        self.add_log("✓ 재로그인 성공")
                    else:
                        self.add_log("✗ 재로그인 실패")
                        self.is_srt_running = False
                        return
                except Exception as e:
                    self.add_log(f"✗ 세션 초기화 중 오류: {str(e)}")
                    self.is_srt_running = False
                    return

            try:
                # 선택한 모든 열차를 한 번에 시도
                train_numbers = ", ".join([t.train_number for t in selected_trains])
                self.add_log(f"  → 열차 예약 시도 중: {train_numbers}")

                request = ReservationRequest(
                    departure_station=selected_trains[0].departure_station,
                    arrival_station=selected_trains[0].arrival_station,
                    departure_date=selected_trains[0].departure_time.date(),
                    departure_time=selected_trains[0].departure_time.strftime("%H%M%S"),
                    passengers=passengers,
                    train_type=TrainType.SRT,
                    is_special_seat_allowed=self.srt_special_seat_check.isChecked(),
                    is_only_special_seat=self.srt_only_special_seat_check.isChecked()
                )
                reservation = self.srt_service.reserve_train(selected_trains, request)
                if reservation.success:
                    self.add_log(f"  ✓ 예약 성공! (열차: {reservation.train_schedule.train_number})")
                    self.add_log(f"  예약번호: {reservation.reservation_number}")

                    # 결제 정보 검증
                    if not self._validate_srt_payment_info():
                        self.add_log("  ✗ 예약은 완료되었으나 결제 정보가 입력되지 않았습니다.")
                        self.add_log(f"    예약번호: {reservation.reservation_number}")
                        self.add_log("    알림음 중지 버튼을 눌러 알림음을 중지하고")
                        self.add_log("    앱에 들어가 10분 내에 결제해주세요.")
                        self.is_srt_running = False  # 예약 루프 중지
                        # 반복 알림음 재생 시작
                        self.alert_thread = threading.Thread(target=self._play_alert_sound_loop, daemon=True)
                        self.alert_thread.start()
                        # 시그널로 알림음 중지 버튼 표시
                        self.log_signals.show_alert_button.emit()
                        return  # 예약 루프 종료

                    # 결제 진행
                    payment = self._process_srt_payment(reservation)

                    if payment.success:
                        self.add_log(f"  ✓ 결제 완료!")
                        self.is_srt_running = False
                        # 버튼 상태 업데이트
                        QTimer.singleShot(0, lambda: self.srt_start_btn.setEnabled(True))
                        QTimer.singleShot(0, lambda: self.srt_stop_btn.setEnabled(False))
                        return  # 예약 루프 종료
                    else:
                        self.add_log("  ✗ 예약은 완료되었으나 결제에 실패했습니다.")
                        self.add_log(f"    예약번호: {payment.reservation_number}")
                        self.add_log("    알림음 중지 버튼을 눌러 알림음을 중지하고")
                        self.add_log("    앱에 들어가 10분 내에 결제해주세요.")
                        self.is_srt_running = False  # 예약 루프 중지
                        # 반복 알림음 재생 시작
                        self.alert_thread = threading.Thread(target=self._play_alert_sound_loop, daemon=True)
                        self.alert_thread.start()
                        # 시그널로 알림음 중지 버튼 표시
                        self.log_signals.show_alert_button.emit()
                        return  # 예약 루프 종료
                else:
                    self.add_log(f"  ✗ 예약 실패: {reservation.message}")
                    delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                    self.add_log(f"⏳ {delay:.1f}초 후 재시도...")
                    time.sleep(delay)

            except Exception as e:
                self.add_log(f"  ✗ 오류: {str(e)}")
                delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                time.sleep(delay)

    def _play_single_alert_sound(self):
        """OS에 따라 알림음 1회 재생"""
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                import os
                os.system('afplay /System/Library/Sounds/Glass.aiff')
            elif system == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif system == "Linux":
                import os
                os.system('paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null || beep 2>/dev/null')
        except Exception as e:
            print(f"알림음 재생 실패: {e}")

    def _play_alert_sound_loop(self):
        """알림음을 반복 재생 (정지 버튼을 누를 때까지)"""
        self.is_alert_playing = True
        while self.is_alert_playing:
            self._play_single_alert_sound()
            time.sleep(1)  # 소리 간격 (1초)

    def _validate_srt_payment_info(self) -> bool:
        """SRT 결제 정보 검증"""
        card_num = self.srt_payment_card_num_input.text().strip()
        card_pw = self.srt_payment_card_pw_input.text().strip()
        expire = self.srt_payment_expire_input.text().strip()

        # 기본 정보 체크
        if not card_num or not card_pw or not expire:
            return False

        # 법인카드 체크
        if self.srt_payment_corporate_check.isChecked():
            business_num = self.srt_payment_business_num_input.text().strip()
            if not business_num:
                return False
        else:
            birth = self.srt_payment_birth_input.text().strip()
            if not birth:
                return False

        return True

    def _process_srt_payment(self, reservation: ReservationResult) -> PaymentResult:
        """SRT 결제 처리"""
        try:
            self.add_log("💳 결제 진행 중...")

            card_number = self.srt_payment_card_num_input.text()
            card_pw = self.srt_payment_card_pw_input.text()
            is_corporate = self.srt_payment_corporate_check.isChecked()
            validation_number = (
                self.srt_payment_birth_input.text()
                if not is_corporate
                else self.srt_payment_business_num_input.text()
            )
            expire = self.srt_payment_expire_input.text()

            # 결제 API 호출
            credit_card = CreditCard(
                number=card_number,
                password=card_pw,
                validation_number=validation_number,
                expire=expire,
                is_corporate=is_corporate
            )
            payment_result = self.srt_service.payment_reservation(
                reservation,
                credit_card,
            )

            return payment_result
        except Exception as e:
            self.add_log(f"💳 결제 오류: {str(e)}")
            return PaymentResult(success=False, message=f"Payment error: {str(e)}")

    def stop_srt(self):
        """SRT 예약 중지"""
        self.is_srt_running = False
        self.is_alert_playing = False  # 알림음 중지
        self.add_log("⏹ SRT 예약을 중지했습니다")
        self.srt_start_btn.setEnabled(True)
        self.srt_stop_btn.setEnabled(False)

    def stop_alert(self):
        """SRT 알림음 중지"""
        self.is_alert_playing = False
        self.is_srt_running = False  # 예약도 중지
        self.add_log("🔇 알림음을 중지했습니다")
        self.add_log("⏹ SRT 예약을 중지했습니다")
        self.srt_alert_stop_btn.setVisible(False)
        self.srt_start_btn.setVisible(True)
        self.srt_start_btn.setEnabled(True)
        self.srt_stop_btn.setVisible(True)
        self.srt_stop_btn.setEnabled(False)

    def show_alert_stop_button(self):
        """SRT 알림음 중지 버튼 표시 (메인 스레드에서 실행)"""
        self.srt_action_widget.setVisible(True)
        self.srt_start_btn.setVisible(False)
        self.srt_stop_btn.setVisible(False)
        self.srt_alert_stop_btn.setVisible(True)

    def stop_ktx_alert(self):
        """KTX 알림음 중지"""
        self.is_alert_playing = False
        self.is_ktx_running = False  # 예약도 중지
        self.add_log("🔇 알림음을 중지했습니다")
        self.add_log("⏹ KTX 예약을 중지했습니다")
        self.ktx_alert_stop_btn.setVisible(False)
        self.ktx_start_btn.setVisible(True)
        self.ktx_start_btn.setEnabled(True)
        self.ktx_stop_btn.setVisible(True)
        self.ktx_stop_btn.setEnabled(False)

    def show_ktx_alert_stop_button(self):
        """KTX 알림음 중지 버튼 표시 (메인 스레드에서 실행)"""
        self.ktx_action_widget.setVisible(True)
        self.ktx_start_btn.setVisible(False)
        self.ktx_stop_btn.setVisible(False)
        self.ktx_alert_stop_btn.setVisible(True)

    def _validate_ktx_payment_info(self) -> bool:
        """KTX 결제 정보 검증"""
        card_num = self.ktx_payment_card_num_input.text().strip()
        card_pw = self.ktx_payment_card_pw_input.text().strip()
        expire = self.ktx_payment_expire_input.text().strip()

        # 기본 정보 체크
        if not card_num or not card_pw or not expire:
            return False

        # 법인카드 체크
        if self.ktx_payment_corporate_check.isChecked():
            business_num = self.ktx_payment_business_num_input.text().strip()
            if not business_num:
                return False
        else:
            birth = self.ktx_payment_birth_input.text().strip()
            if not birth:
                return False

        return True

    def _process_ktx_payment(self, reservation: ReservationResult) -> PaymentResult:
        """KTX 결제 처리"""
        try:
            self.add_log("💳 결제 진행 중...")

            card_number = self.ktx_payment_card_num_input.text()
            card_pw = self.ktx_payment_card_pw_input.text()
            is_corporate = self.ktx_payment_corporate_check.isChecked()
            validation_number = (
                self.ktx_payment_birth_input.text()
                if not is_corporate
                else self.ktx_payment_business_num_input.text()
            )
            expire = self.ktx_payment_expire_input.text()

            # 결제 API 호출
            credit_card = CreditCard(
                number=card_number,
                password=card_pw,
                validation_number=validation_number,
                expire=expire,
                is_corporate=is_corporate
            )
            payment_result = self.ktx_service.payment_reservation(
                reservation,
                credit_card,
            )

            return payment_result
        except Exception as e:
            self.add_log(f"💳 결제 오류: {str(e)}")
            return PaymentResult(success=False, message=f"Payment error: {str(e)}")


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 모던한 스타일 적용
    setup_dark_palette(app)  # 다크 팔레트 강제 적용 (Windows 시스템 테마 무시)
    window = TrainReservationApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()