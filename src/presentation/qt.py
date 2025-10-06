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
    QCheckBox, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon
from domain.models.entities import ReservationRequest, Passenger, TrainSchedule, ReservationResult, CreditCard, PaymentResult
from domain.models.enums import PassengerType, TrainType
from src.infrastructure.adapters.ktx_service import KTXService
from src.infrastructure.adapters.srt_service import SRTService
from src.constants.ui import (
    DEFAULT_DEPARTURE_DATE, DEFAULT_KTX_TIME, DEFAULT_SRT_TIME,
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


STYLESHEET = """
* {
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "맑은 고딕", "Malgun Gothic", "Segoe UI", sans-serif;
}

QMainWindow {
    background: #0e1621;
}

#centralWidget {
    background: #17212b;
    border-radius: 0px;
}

/* 탭 스타일 - Telegram 느낌 */
QTabWidget::pane {
    border: none;
    background: #17212b;
    border-radius: 0px;
}

QTabBar::tab {
    background: transparent;
    color: #8b98a5;
    padding: 14px 28px;
    margin-right: 0px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 15px;
    font-weight: 500;
    min-width: 100px;
}

QTabBar::tab:selected {
    background: transparent;
    color: #5288c1;
    border-bottom: 2px solid #5288c1;
}

QTabBar::tab:hover:!selected {
    color: #a8b4c0;
}

/* 헤더 */
QLabel#titleLabel {
    font-size: 26px;
    font-weight: 600;
    color: #ffffff;
    padding: 20px;
    background: transparent;
}

QLabel#sectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    padding: 4px 0;
    background: transparent;
}

QLabel {
    color: #8b98a5;
    font-size: 13px;
    background: transparent;
}

/* 카드 */
QFrame#card {
    background: #232e3c;
    border-radius: 10px;
    border: 1px solid #2b3745;
}

/* 입력 필드 - Telegram 스타일 */
QLineEdit {
    padding: 12px 14px;
    border: none;
    border-radius: 8px;
    background: #232e3c;
    color: #ffffff;
    font-size: 14px;
    selection-background-color: #5288c1;
}

QLineEdit:focus {
    background: #2b3745;
    border: 1px solid #5288c1;
}

QLineEdit::placeholder {
    color: #5d6d7e;
}

/* 버튼 - Telegram 스타일 */
QPushButton {
    padding: 11px 22px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    min-height: 42px;
}

QPushButton#primaryButton {
    background: #5288c1;
    color: #ffffff;
}

QPushButton#primaryButton:hover {
    background: #6b9fd8;
}

QPushButton#primaryButton:pressed {
    background: #4a7bad;
}

QPushButton#primaryButton:disabled {
    background: #3d4f5f;
    color: #5d6d7e;
}

QPushButton#searchButton {
    background: #5288c1;
    color: #ffffff;
}

QPushButton#searchButton:hover {
    background: #6b9fd8;
}

QPushButton#searchButton:pressed {
    background: #4a7bad;
}

QPushButton#stopButton {
    background: #e74c3c;
    color: #ffffff;
}

QPushButton#stopButton:hover {
    background: #ec7063;
}

QPushButton#stopButton:pressed {
    background: #c0392b;
}

QPushButton#clearButton {
    background: transparent;
    color: #5288c1;
    padding: 6px 14px;
    min-height: 28px;
    font-size: 13px;
    border: 1px solid #2b3745;
}

QPushButton#clearButton:hover {
    background: #232e3c;
}

/* 체크박스 - Telegram 스타일 */
QCheckBox {
    spacing: 10px;
    font-size: 14px;
    color: #e4e9ed;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid #5d6d7e;
    background: transparent;
}

QCheckBox::indicator:checked {
    background: #5288c1;
    border: 2px solid #5288c1;
}

QCheckBox::indicator:hover {
    border: 2px solid #5288c1;
}

/* 로그 디스플레이 - Telegram 다크 모드 */
QTextEdit#logDisplay {
    background: #0e1621;
    color: #8ec677;
    border: none;
    border-radius: 8px;
    padding: 14px;
    font-family: "SF Mono", "Monaco", "Consolas", "Courier New", monospace;
    font-size: 12px;
    line-height: 1.5;
}

/* 스크롤바 - 미니멀 */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #3d4f5f;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #4a6075;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #3d4f5f;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #4a6075;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 열차 항목 - Telegram 메시지 스타일 */
QFrame#trainItem {
    background: #232e3c;
    border: 1px solid #2b3745;
    border-radius: 8px;
}

QFrame#trainItem:hover {
    background: #2b3745;
    border: 1px solid #5288c1;
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
        self.ktx_pw_input.setInputMethodHints(Qt.InputMethodHint.ImhLatinOnly)

        self.ktx_pw_toggle_btn = QPushButton("Show")
        self.ktx_pw_toggle_btn.setFixedWidth(60)
        self.ktx_pw_toggle_btn.setObjectName("clearButton")
        self.ktx_pw_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.ktx_pw_input, self.ktx_pw_toggle_btn))

        ktx_pw_layout.addWidget(self.ktx_pw_input)
        ktx_pw_layout.addWidget(self.ktx_pw_toggle_btn)

        login_card.add_widget(self.ktx_id_input)
        login_card.add_layout(ktx_pw_layout)
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

        self.ktx_date_input = QLineEdit(DEFAULT_DEPARTURE_DATE)
        self.ktx_date_input.setPlaceholderText("YYYYMMDD")
        self.ktx_time_input = QLineEdit(
            datetime.datetime.strptime(DEFAULT_KTX_TIME, "%H%M%S").strftime("%H%M")
        )
        self.ktx_time_input.setPlaceholderText("HHMM")

        grid.addWidget(QLabel("출발일"), 1, 0)
        grid.addWidget(self.ktx_date_input, 1, 1)
        grid.addWidget(QLabel("출발시간"), 1, 2)
        grid.addWidget(self.ktx_time_input, 1, 3)

        search_card.add_layout(grid)

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
        self.srt_pw_input.setInputMethodHints(Qt.InputMethodHint.ImhLatinOnly)

        self.srt_pw_toggle_btn = QPushButton("Show")
        self.srt_pw_toggle_btn.setFixedWidth(60)
        self.srt_pw_toggle_btn.setObjectName("clearButton")
        self.srt_pw_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.srt_pw_input, self.srt_pw_toggle_btn))

        srt_pw_layout.addWidget(self.srt_pw_input)
        srt_pw_layout.addWidget(self.srt_pw_toggle_btn)

        login_card.add_widget(self.srt_id_input)
        login_card.add_layout(srt_pw_layout)
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

        self.srt_date_input = QLineEdit(DEFAULT_DEPARTURE_DATE)
        self.srt_date_input.setPlaceholderText("YYYYMMDD")
        self.srt_time_input = QLineEdit(
            datetime.datetime.strptime(DEFAULT_SRT_TIME, "%H%M%S").strftime("%H%M")
        )
        self.srt_time_input.setPlaceholderText("HHMM")

        grid.addWidget(QLabel("출발일"), 1, 0)
        grid.addWidget(self.srt_date_input, 1, 1)
        grid.addWidget(QLabel("출발시간"), 1, 2)
        grid.addWidget(self.srt_time_input, 1, 3)

        search_card.add_layout(grid)

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
        card = SectionCard("📋 실행 로그")

        # 클리어 버튼
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        clear_btn = QPushButton("🗑️ 지우기")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(clear_btn)
        card.add_layout(header_layout)

        # 로그 디스플레이
        self.log_display = QTextEdit()
        self.log_display.setObjectName("logDisplay")
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(200)
        self.log_display.setMaximumHeight(250)
        card.add_widget(self.log_display)

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
            QTimer.singleShot(0, lambda: QMessageBox.warning(
                self,
                "입력 오류",
                "아이디와 비밀번호를 입력해주세요."
            ))
            return

        self.ktx_search_btn.setEnabled(False)
        self.add_log("🔐 KTX 로그인 중...")

        try:
            login_result = self.ktx_service.login(self.ktx_id_input.text(), self.ktx_pw_input.text())

            if not login_result:
                self.add_log("✗ 로그인 실패")
                QTimer.singleShot(0, lambda: QMessageBox.critical(
                    self,
                    "로그인 실패",
                    "아이디 또는 비밀번호가 올바르지 않습니다."
                ))
                self.ktx_search_btn.setEnabled(True)
                return

            self.add_log("✓ 로그인 성공")
            self.add_log("🔍 열차 검색 중...")

            departure_date = datetime.datetime.strptime(self.ktx_date_input.text(), "%Y%m%d").date()
            departure_time = self.ktx_time_input.text() + "00"

            request = ReservationRequest(
                departure_station=self.ktx_dep_input.text(),
                arrival_station=self.ktx_arr_input.text(),
                departure_date=departure_date,
                departure_time=departure_time,
                passengers=[Passenger(PassengerType.ADULT, 1)],
                train_type=TrainType.KTX
            )

            trains = self.ktx_service.search_trains(request)
            self.ktx_trains = trains

            if trains:
                self.add_log(f"✓ {len(trains)}개의 열차를 찾았습니다")
                QTimer.singleShot(0, self.display_ktx_trains)
            else:
                self.add_log("✗ 열차를 찾을 수 없습니다")

        except Exception as e:
            self.add_log(f"✗ 오류: {str(e)}")
            QTimer.singleShot(0, lambda: QMessageBox.critical(
                self,
                "오류",
                f"로그인 중 오류가 발생했습니다.\n{str(e)}"
            ))

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

        while self.is_ktx_running:
            attempt += 1
            self.add_log(f"🔄 예약 시도 #{attempt}")

            for train in selected_trains:
                if not self.is_ktx_running:
                    break

                try:
                    self.add_log(f"  → {train.train_number} 예약 시도 중...")

                    request = ReservationRequest(
                        departure_station=train.departure_station,
                        arrival_station=train.arrival_station,
                        departure_date=train.departure_time.date(),
                        departure_time=train.departure_time.strftime("%H%M%S"),
                        passengers=[Passenger(PassengerType.ADULT, 1)],
                        train_type=TrainType.KTX
                    )
                    reservation = self.ktx_service.reserve_train(train, request)
                    if reservation.success:
                        self.add_log(f"  ✓ {train.train_number} 예약 성공!")
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
                            return  # 다른 열차는 시도하지 않고 종료

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
                            return  # 다른 열차는 시도하지 않고 종료
                    else:
                        self.add_log(f"  ✗ {train.train_number} 예약 실패: {reservation.message}")

                except Exception as e:
                    self.add_log(f"  ✗ 오류: {str(e)}")

            if self.is_ktx_running:
                delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                self.add_log(f"⏳ {delay:.1f}초 후 재시도...")
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
            QTimer.singleShot(0, lambda: QMessageBox.warning(
                self,
                "입력 오류",
                "아이디와 비밀번호를 입력해주세요."
            ))
            return

        self.srt_search_btn.setEnabled(False)
        self.add_log("🔐 SRT 로그인 중...")

        try:
            login_result = self.srt_service.login(self.srt_id_input.text(), self.srt_pw_input.text())

            if not login_result:
                self.add_log("✗ 로그인 실패")
                QTimer.singleShot(0, lambda: QMessageBox.critical(
                    self,
                    "로그인 실패",
                    "아이디 또는 비밀번호가 올바르지 않습니다."
                ))
                self.srt_search_btn.setEnabled(True)
                return

            self.add_log("✓ 로그인 성공")
            self.add_log("🔍 열차 검색 중...")

            departure_date = datetime.datetime.strptime(self.srt_date_input.text(), "%Y%m%d").date()
            departure_time = self.srt_time_input.text() + "00"

            request = ReservationRequest(
                departure_station=self.srt_dep_input.text(),
                arrival_station=self.srt_arr_input.text(),
                departure_date=departure_date,
                departure_time=departure_time,
                passengers=[Passenger(PassengerType.ADULT, 1)],
                train_type=TrainType.SRT
            )

            trains = self.srt_service.search_trains(request)
            self.srt_trains = trains

            if trains:
                self.add_log(f"✓ {len(trains)}개의 열차를 찾았습니다")
                QTimer.singleShot(0, self.display_srt_trains)
            else:
                self.add_log("✗ 열차를 찾을 수 없습니다")

        except Exception as e:
            self.add_log(f"✗ 오류: {str(e)}")
            QTimer.singleShot(0, lambda: QMessageBox.critical(
                self,
                "오류",
                f"로그인 중 오류가 발생했습니다.\n{str(e)}"
            ))

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

        while self.is_srt_running:
            attempt += 1
            self.add_log(f"🔄 예약 시도 #{attempt}")

            for train in selected_trains:
                if not self.is_srt_running:
                    break

                try:
                    self.add_log(f"  → {train.train_number} 예약 시도 중...")
                    request = ReservationRequest(
                        departure_station=train.departure_station,
                        arrival_station=train.arrival_station,
                        departure_date=train.departure_time.date(),
                        departure_time=train.departure_time.strftime("%H%M%S"),
                        passengers=[Passenger(PassengerType.ADULT, 1)],
                        train_type=TrainType.SRT
                    )
                    reservation = self.srt_service.reserve_train(train, request)
                    if reservation.success:
                        self.add_log(f"  ✓ {train.train_number} 예약 성공!")
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
                            return  # 다른 열차는 시도하지 않고 종료

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
                            return  # 다른 열차는 시도하지 않고 종료
                    else:
                        self.add_log(f"  ✗ {train.train_number} 예약 실패: {reservation.message}")

                except Exception as e:
                    self.add_log(f"  ✗ 오류: {str(e)}")

            if self.is_srt_running:
                delay = random.uniform(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                self.add_log(f"⏳ {delay:.1f}초 후 재시도...")
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

            return payment_result  # 임시로 True 반환
        except Exception as e:
            self.add_log(f"💳 결제 오류: {str(e)}")
            return False

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
    window = TrainReservationApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()