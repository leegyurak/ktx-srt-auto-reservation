"""Unit tests for Qt presentation layer components"""
import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import Qt


@pytest.mark.unit
@pytest.mark.ui
class TestLogSignals:
    """Tests for LogSignals class"""

    @pytest.fixture
    def log_signals(self):
        """Create LogSignals instance"""
        from src.presentation.qt import LogSignals
        return LogSignals()

    def test_log_signals_has_required_signals(self, log_signals):
        """Test that LogSignals has all required signals"""
        assert hasattr(log_signals, 'log_message')
        assert hasattr(log_signals, 'show_alert_button')
        assert hasattr(log_signals, 'show_ktx_alert_button')

    def test_log_message_signal_can_emit(self, log_signals):
        """Test that log_message signal can emit"""
        received = []

        def handler(msg):
            received.append(msg)

        log_signals.log_message.connect(handler)
        log_signals.log_message.emit("Test message")

        assert len(received) == 1
        assert received[0] == "Test message"


@pytest.mark.unit
@pytest.mark.ui
class TestTrainItemWidget:
    """Tests for TrainItemWidget"""

    @pytest.fixture
    def train_widget(self, qtbot):
        """Create TrainItemWidget instance"""
        from src.presentation.qt import TrainItemWidget
        widget = TrainItemWidget("Test Train | 10:00 → 12:30")
        qtbot.addWidget(widget)
        return widget

    def test_train_widget_initialization(self, train_widget):
        """Test TrainItemWidget initializes correctly"""
        assert train_widget is not None
        assert train_widget.checkbox is not None
        assert train_widget.label is not None

    def test_train_widget_label_text(self, train_widget):
        """Test TrainItemWidget displays correct label text"""
        assert train_widget.label.text() == "Test Train | 10:00 → 12:30"

    def test_train_widget_checkbox_unchecked_by_default(self, train_widget):
        """Test checkbox is unchecked by default"""
        assert train_widget.checkbox.isChecked() is False

    def test_train_widget_checkbox_can_be_checked(self, train_widget, qtbot):
        """Test checkbox can be checked"""
        # Directly set checked state (more reliable than simulated click)
        train_widget.checkbox.setChecked(True)
        assert train_widget.checkbox.isChecked() is True

        # Test unchecking
        train_widget.checkbox.setChecked(False)
        assert train_widget.checkbox.isChecked() is False


@pytest.mark.unit
@pytest.mark.ui
class TestSectionCard:
    """Tests for SectionCard widget"""

    @pytest.fixture
    def section_card(self, qtbot):
        """Create SectionCard instance"""
        from src.presentation.qt import SectionCard
        card = SectionCard("Test Section")
        qtbot.addWidget(card)
        return card

    def test_section_card_initialization(self, section_card):
        """Test SectionCard initializes correctly"""
        assert section_card is not None
        assert section_card.objectName() == "card"

    def test_section_card_can_add_widget(self, section_card):
        """Test SectionCard can add widgets"""
        from PyQt6.QtWidgets import QLabel
        label = QLabel("Test Label")
        section_card.add_widget(label)
        # Widget should be added to layout
        assert label.parent() == section_card


@pytest.mark.unit
@pytest.mark.ui
class TestResourcePath:
    """Tests for resource_path function"""

    def test_resource_path_returns_absolute_path(self):
        """Test that resource_path returns an absolute path"""
        from src.presentation.qt import resource_path
        import os
        path = resource_path('test.txt')
        assert os.path.isabs(path)

    def test_resource_path_combines_paths_correctly(self):
        """Test that resource_path combines paths correctly"""
        from src.presentation.qt import resource_path
        path = resource_path('assets/favicon.ico')
        assert 'assets' in path
        assert 'favicon.ico' in path

    @patch('sys._MEIPASS', '/fake/path', create=True)
    def test_resource_path_uses_meipass_when_available(self):
        """Test that resource_path uses _MEIPASS when available"""
        from src.presentation.qt import resource_path
        path = resource_path('test.txt')
        assert '/fake/path' in path


@pytest.mark.unit
@pytest.mark.ui
class TestDarkPalette:
    """Tests for dark mode palette setup"""

    def test_setup_dark_palette_sets_colors(self, qapp):
        """Test that setup_dark_palette sets palette colors"""
        from src.presentation.qt import setup_dark_palette
        from PyQt6.QtGui import QPalette

        setup_dark_palette(qapp)
        palette = qapp.palette()

        # Check that some colors are set
        window_color = palette.color(QPalette.ColorRole.Window)
        assert window_color is not None

    def test_dark_palette_has_dark_background(self, qapp):
        """Test that dark palette has dark background colors"""
        from src.presentation.qt import setup_dark_palette
        from PyQt6.QtGui import QPalette

        setup_dark_palette(qapp)
        palette = qapp.palette()

        window_color = palette.color(QPalette.ColorRole.Window)
        # Dark colors have low RGB values
        assert window_color.red() < 100
        assert window_color.green() < 100
        assert window_color.blue() < 100
