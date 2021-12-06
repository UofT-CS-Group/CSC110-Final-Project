"""
This module contains some GUI utilities like classes and helper methods for our project.
"""
# Python built-ins
import datetime
from typing import Iterable, Optional

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Matplotlib
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

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

    def __init__(self, text: str = 'Standard Label', parent: Optional[QWidget] = None):
        super(StandardLabel, self).__init__(text, parent)
        set_font(self)


class StandardPushButton(QPushButton):
    """
    A standard push button for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, text: str = 'Push Button', parent: Optional[QWidget] = None):
        super(StandardPushButton, self).__init__(text, parent)
        set_font(self)


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

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(StandardDateEdit, self).__init__(parent)
        set_font(self)

    def set_extremum_date(self, minimum: datetime.date, maximum: datetime.date):
        self.setMinimumDate(minimum)
        self.setMaximumDate(maximum)


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
        set_font(self)


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
        set_font(self)


class StandardTabWidget(QTabWidget):
    """
    A standard tab widget for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super(StandardTabWidget, self).__init__(parent)
        set_font(self)


class StandardLineEdit(QLineEdit):
    """
    A standard line edit for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, contents: str = '', parent: Optional[QWidget] = None) -> None:
        super().__init__(contents, parent)
        set_font(self)


class StandardMenuBar(QMenuBar):
    """
    A standard menu bar for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(StandardMenuBar, self).__init__(parent)
        set_font(self, font_size=12)


class StandardNavigationToolbar(NavigationToolbar):
    """
    A standard menu for our project.

    When needed, we could add more attributes and methods.
    """
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Pan', 'Zoom')]


class StandardColorDialog(QColorDialog):
    """
    A standard color dialog for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(StandardColorDialog, self).__init__(parent)
        set_font(self, font_size=12)


class StandardInputDialog(QInputDialog):
    """
    A standard input dialog for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(StandardInputDialog, self).__init__(parent)
        set_font(self, font_size=12)


class StandardFileDialog(QFileDialog):
    """
    A standard file dialog for our project.

    When needed, we could add more attributes and methods.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super(StandardFileDialog, self).__init__(parent)
        set_font(self, font_size=12)
