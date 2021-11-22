"""
This module contains some GUI utilities like classes and helper methods for our project.
"""
# Python built-ins
from typing import Iterable, Optional

# PyQt5
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Our modules
import settings


# =================================================================================================
# Helper Functions
# =================================================================================================


def set_font(widget: QWidget,
             font_family: str = settings.FONT_FAMILY,
             font_size: int = settings.FONT_SIZE) -> None:
    """
    Set the font of given widget to given font and size.

    Note:
        - By default, it will set the font of the given widget to the font settings specified in
        settings.py
    """
    font: QFont = widget.font()
    font.setFamily(font_family)
    font.setPointSize(font_size)
    widget.setFont(font)


# =================================================================================================
# Utility Classes
# =================================================================================================


class StandardLabel(QLabel):
    """
    A standard label for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, text: str = 'Standard Label'):
        super(StandardLabel, self).__init__()
        set_font(self)

        # Set Default Text
        self.setText(text)


class StandardPushButton(QPushButton):
    """
    A standard push button for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, text: str = 'Push Button', *args):
        super(StandardPushButton, self).__init__(*args)
        set_font(self)
        self.setText(text)


class StandardComboBox(QComboBox):
    """
    A standard combo box for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None, items: Optional[Iterable[str]] = None):
        super(StandardComboBox, self).__init__(parent)
        set_font(self)
        if items is not None:
            self.addItems(items)

    def clear_and_disable(self):
        self.clear()
        self.setEnabled(False)

    def enable_and_add_items(self, items: Optional[Iterable[str]] = None):
        self.setEnabled(True)
        if items is not None:
            self.addItems(items)


class StandardDateEdit(QDateEdit):
    """
    A standard date edit for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, *args) -> None:
        super(StandardDateEdit, self).__init__(*args)
        set_font(self)


class StandardCheckbox(QCheckBox):
    """
    A standard checkbox for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, text: str = 'Check Box', parent: Optional[QWidget] = None) -> None:
        super(StandardCheckbox, self).__init__(text, parent)
        set_font(self)


class StandardRadioButton(QRadioButton):
    """
    A standard radio button for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, text: str = 'Radio Button', parent: Optional[QWidget] = None):
        super(StandardRadioButton, self).__init__(text, parent)
        set_font(self)


class StandardProgressBar(QProgressBar):
    """
    A standard progress bar for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super(StandardProgressBar, self).__init__(parent)
        set_font(self)


class StandardGroupBox(QGroupBox):
    """
    A standard group box for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, title: str = 'Group Box', parent: Optional[QWidget] = None):
        super(StandardGroupBox, self).__init__(title, parent)


class StandardSlider(QSlider):
    """
    A standard slider for our project.

    - Note:
        - By default, it's a horizontal slider.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal,
                 parent: Optional[QWidget] = None):
        super(StandardSlider, self).__init__(orientation, parent)


class StandardTabWidget(QTabWidget):
    """
    A standard tab widget for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super(StandardTabWidget, self).__init__(parent)
