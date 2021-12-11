"""
This module contains some GUI utilities like classes and helper methods for our project.
"""
# Python built-ins
import datetime
import typing
from typing import Callable, Iterable, List, Optional, Union

# PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# Our modules
import settings

# =================================================================================================
# Constants
# =================================================================================================

# A dict that maps line styles to their descriptions.
LINE_STYLES = {
    'solid'  : 'Solid',
    'dashed' : 'Dashed',
    'dashdot': 'Dash-dot',
    'dotted' : 'Dotted'
}

# Special markers copied from matplotlib.markers.py.
(TICKLEFT, TICKRIGHT, TICKUP, TICKDOWN,
 CARETLEFT, CARETRIGHT, CARETUP, CARETDOWN,
 CARETLEFTBASE, CARETRIGHTBASE, CARETUPBASE, CARETDOWNBASE) = range(12)

# A dict that maps the line markers to tuples representing the description of the marker and the
# icon resource name.
LINE_MARKERS = {
    '.'           : ('Point', 'm00.webp',),
    ','           : ('Pixel', 'm01.webp',),
    'o'           : ('Circle', 'm02.webp',),
    'v'           : ('Triangle Down', 'm03.webp',),
    '^'           : ('Triangle Up', 'm04.webp',),
    '<'           : ('Triangle Left', 'm05.webp',),
    '>'           : ('Triangle Right', 'm06.webp',),
    '1'           : ('tri_down', 'm07.webp',),
    '2'           : ('tri_up', 'm08.webp',),
    '3'           : ('tri_left', 'm09.webp',),
    '4'           : ('tri_right', 'm10.webp',),
    '8'           : ('Octagon', 'm11.webp',),
    's'           : ('Square', 'm12.webp',),
    'p'           : ('Pentagon', 'm13.webp',),
    '*'           : ('Star', 'm14.webp',),
    'h'           : ('Hexagon1', 'm15.webp',),
    'H'           : ('Hexagon2', 'm16.webp',),
    '+'           : ('Plus', 'm17.webp',),
    'x'           : ('x', 'm18.webp',),
    'D'           : ('Diamond', 'm19.webp',),
    'd'           : ('Thin Diamond', 'm20.webp',),
    '|'           : ('Vertical Line', 'm21.webp',),
    '_'           : ('Horizontal Line', 'm22.webp',),
    'P'           : ('Plus Filled', 'm23.webp',),
    'X'           : ('X Filled', 'm24.webp',),
    TICKLEFT      : ('Tick Left', 'm25.webp',),
    TICKRIGHT     : ('Tick Right', 'm26.webp',),
    TICKUP        : ('Tick Up', 'm27.webp',),
    TICKDOWN      : ('Tick Down', 'm28.webp',),
    CARETLEFT     : ('Caret Left', 'm29.webp',),
    CARETRIGHT    : ('Caret Right', 'm30.webp',),
    CARETUP       : ('Caret Up', 'm31.webp',),
    CARETDOWN     : ('Caret Down', 'm32.webp',),
    CARETLEFTBASE : ('Caret Left Base', 'm33.webp',),
    CARETRIGHTBASE: ('Caret Right Base', 'm34.webp',),
    CARETUPBASE   : ('Caret Up Base', 'm35.webp',),
    CARETDOWNBASE : ('Caret Down Base', 'm36.webp'),
    "None"        : ('No Marker', ''),
}


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
    # Getting available fonts
    font_base = QFontDatabase()
    fonts = font_base.families()

    font: QFont = widget.font()

    # There's only two possibilities, either the user is in Windows, which uses Calibri
    if font_family in fonts:
        font.setFamily(font_family)

    # Or the user is in Mac, which uses Helvetica
    else:
        font.setFamily(settings.ALT_FONT_FAMILY)

    font.setPointSize(font_size)
    widget.setFont(font)


def make_function(target: Callable, *args, **kwargs) -> Callable:
    """
    Return a wrapper function without any parameters that calls the target with args and kwargs.
    The returned function could avoid Python late binding features.
    """
    def function():
        target(*args, **kwargs)

    return function


# =================================================================================================
# Utility Classes
# =================================================================================================


class EnhancedVBoxLayout(QVBoxLayout):
    """
    An enhanced QVBoxLayout, and it maintains a list of QHLayouts as the rows of the QVBoxLayout.
    """

    horizontal_layouts: List[QHBoxLayout]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.horizontal_layouts = []

    def add_row(self, stretch: int = 0) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.horizontal_layouts.append(layout)
        self.addLayout(layout, stretch)
        return layout

    def add_widget(self, widget: QWidget, row: int, stretch: int = 0,
                   alignment: Union[Qt.Alignment, Qt.AlignmentFlag] = Qt.Alignment()) -> None:
        length = len(self.horizontal_layouts)

        if row > length:
            raise IndexError('Invalid row value!')
        elif row == length:
            self.add_row()

        self.horizontal_layouts[row].addWidget(widget, stretch, alignment)


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
