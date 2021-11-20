"""
Main GUI + backend here
I know it's in efficient and shitty
Just for temp use
"""
import datetime
import math
import time
from typing import Iterable, List, Optional

import matplotlib.backend_bases
import matplotlib.lines
import matplotlib.style
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import algorithms
import data
import main
import settings

matplotlib.style.use('fast')


# =================================================================================================
# Helper functions and classes.
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


def set_title_font(widget: QWidget,
                   font_family: str = settings.FONT_FAMILY,
                   font_size: int = settings.FONT_SIZE_RESEARCH_QUESTION) -> None:
    """
    Set the font of the title (our research question) to given font and size.

    Note:
        - By default, it will set the font of the title (our research question) to
        the font settings specified in settings.py
    """
    font: QFont = widget.font()
    font.setFamily(font_family)
    font.setPointSize(font_size)
    font.setBold(True)
    widget.setFont(font)


class StandardLabel(QLabel):
    """
    A standard label for our project.
    
    When needed, we could add more attributes and functions.
    """

    def __init__(self, text: str = ''):
        super(StandardLabel, self).__init__()
        set_font(self)

        # Set Default Text
        self.setText(text)

    def set_research_question_font(self) -> None:
        """
        Set the font of the title (our research question).
        """
        set_title_font(self)


class StandardPushButton(QPushButton):
    """
    A standard push button for our project.
    
    When needed, we could add more attributes and functions.
    """

    def __init__(self, text: str = '', *__args):
        super().__init__(*__args)
        set_font(self)
        self.setText(text)


class StandardComboBox(QComboBox):
    """
    A standard combo box for our project.
    
    When needed, we could add more attributes and functions.
    """

    def __init__(self, parent=None, items: Iterable = None):
        super().__init__(parent)
        set_font(self)
        if items is not None:
            self.addItems(items)

        # Set the field width to avoid omitting
        self.setStyleSheet(f'QAbstractItemView::item {qSetFieldWidth(50)}')
        self.setView(QListView())

    def clear_and_disable(self):
        self.clear()
        self.setEnabled(False)

    def enable_and_add_items(self, texts: Iterable[str]):
        self.setEnabled(True)
        self.addItems(texts)


class StandardDateEdit(QDateEdit):
    """
    A standard date edit for our project.
    
    When needed, we could add more attributes and functions.
    """

    def __init__(self, *__args) -> None:
        super().__init__(*__args)
        set_font(self)


class StandardCheckbox(QCheckBox):
    """
    A standard checkbox for our project.

    When needed, we could add more attributes and functions.
    """

    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        set_font(self)


class StandardProgressBar(QProgressBar):
    """
    A standard progress bar for our project.

    When needed, we could add more attributes and functions.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super(StandardProgressBar, self).__init__(parent)
        set_font(self)


# =================================================================================================
# Main window.
# =================================================================================================


class PlotCanvas(FigureCanvas):
    """
    Figure widget from matplotlib with a cross-hair.
    """

    figure: pyplot.Figure
    axes_covid: pyplot.Axes
    axes_closure: pyplot.Axes

    covid_x_data: List[datetime.date]
    covid_y_data: List[int]

    closure_x_data: List[datetime.date]
    closure_y_data: List[int]

    is_covid_cross_hair_init: bool = False
    covid_horizontal_cross_hair: matplotlib.lines.Line2D
    covid_vertical_cross_hair: matplotlib.lines.Line2D

    is_closure_cross_hair_init: bool = False
    closure_horizontal_cross_hair: matplotlib.lines.Line2D
    closure_vertical_cross_hair: matplotlib.lines.Line2D

    def __init__(self) -> None:
        self.figure = pyplot.Figure(tight_layout=True, linewidth=1)
        self.axes_covid, self.axes_closure = self.figure.subplots(1, 2)

        super(PlotCanvas, self).__init__(self.figure)
        self.mpl_connect("motion_notify_event", self.on_mouse_move)

        # Initialize curr_x and curr_y to None and updated from the on_mouse_move function
        self.curr_x = None
        self.curr_y = None

        # Formatting the right upper corner of the display
        self.axes_covid.format_coord = lambda _, __: \
            f'Date = {self.curr_x}, Cases = {self.curr_y}'
        self.axes_closure.format_coord = lambda _, __: \
            f'Date = {self.curr_x}, Status = ' \
            f'{data.ENUM_TO_STATUS_DICT[data.ClosureStatus(self.curr_y)]}'
        self.draw()

    def plot_covid_cases(self, covid_cases: List[data.CovidCaseData]) -> None:
        """Plots the COVID Data in self.axes_covid"""
        x_axis = [c.date for c in covid_cases]
        y_axis = [c.cases for c in covid_cases]
        self.covid_x_data = x_axis
        self.covid_y_data = y_axis
        self.axes_covid.clear()
        self.axes_covid.plot(x_axis, y_axis, marker='.', color='orange')
        for text in self.axes_covid.get_xticklabels():
            text.set_rotation(40.0)

        # Setting labels and title
        self.axes_covid.set_title('COVID-19 Cases')
        self.axes_covid.set_xlabel('Dates')
        self.axes_covid.set_ylabel('Cumulative cases')

        self.draw()
        self.is_covid_cross_hair_init = False

    def plot_school_closures(self, school_closures: List[data.SchoolClosureData]) -> None:
        """Plots the Closure Data in self.axes_closure"""
        x_axis = [c.date for c in school_closures]
        y_axis = [c.status.value for c in school_closures]
        self.closure_x_data = x_axis
        self.closure_y_data = y_axis
        self.axes_closure.clear()
        self.axes_closure.plot(x_axis, y_axis, marker='.', color='green')
        self.axes_closure.set_yticks(ticks=[0, 1, 2, 3], minor=False)
        self.axes_closure.set_yticklabels(
                labels=['Academic Break', 'Fully Open', 'Partially Open', 'Closed'],
                minor=False)
        for text in self.axes_closure.get_xticklabels():
            text.set_rotation(40.0)

        # Setting labels and title
        self.axes_closure.set_title('School Closure Status')
        self.axes_closure.set_xlabel('Dates')

        self.draw()
        self.is_closure_cross_hair_init = False

    def on_mouse_move(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """The handler of on_mouse_move event, renders the crosshair"""
        # The reason why the cross-hair is laggy is because self.draw()
        # takes a very long time to draw.
        # This part of code is a little bit shitty, but it is not worthy to fix
        if event.inaxes:
            x = event.xdata
            x = datetime.timedelta(days=x)
            x_date = datetime.date.fromtimestamp(0) + x
            if event.inaxes == self.axes_covid:
                index = algorithms.binary_search(self.covid_x_data, x_date)
                x = self.covid_x_data[index]
                # I don't know why it works, but it works.
                y = self.covid_y_data[min(index + 1, len(self.covid_y_data) - 1)]
                real_x = (x - datetime.date.fromtimestamp(0)).days

                if not self.is_covid_cross_hair_init:
                    self.covid_horizontal_cross_hair = self.axes_covid.axhline(
                            y=y, color='black', linewidth=0.8, linestyle='--')
                    self.covid_vertical_cross_hair = self.axes_covid.axvline(
                            x=real_x, color='black', linewidth=0.8, linestyle='--')
                    self.is_covid_cross_hair_init = True

                self.covid_horizontal_cross_hair.set_visible(True)
                self.covid_vertical_cross_hair.set_visible(True)

                self.covid_horizontal_cross_hair.set_ydata(y)
                self.covid_vertical_cross_hair.set_xdata(real_x)

                self.curr_x = x
                self.curr_y = y

                self.draw()
            elif event.inaxes == self.axes_closure:
                index = algorithms.binary_search(self.closure_x_data, x_date)
                x = self.closure_x_data[index]
                y = self.closure_y_data[min(index + 1, len(self.closure_y_data) - 1)]
                real_x = (x - datetime.date.fromtimestamp(0)).days

                if not self.is_closure_cross_hair_init:
                    self.closure_horizontal_cross_hair = self.axes_closure.axhline(
                            y=y, color='black', linewidth=0.8, linestyle='--')
                    self.closure_vertical_cross_hair = self.axes_closure.axvline(
                            x=real_x, color='black', linewidth=0.8, linestyle='--')
                    self.is_closure_cross_hair_init = True

                self.closure_horizontal_cross_hair.set_visible(True)
                self.closure_vertical_cross_hair.set_visible(True)

                self.closure_horizontal_cross_hair.set_ydata(y)
                self.closure_vertical_cross_hair.set_xdata(real_x)

                self.curr_x = x
                self.curr_y = y

                self.draw()
        else:
            if self.is_covid_cross_hair_init:
                if self.covid_horizontal_cross_hair.get_visible() and \
                        self.covid_vertical_cross_hair.get_visible():
                    self.covid_horizontal_cross_hair.set_visible(False)
                    self.covid_vertical_cross_hair.set_visible(False)
                    self.curr_x = None
                    self.curr_y = None
                    self.draw()
            if self.is_closure_cross_hair_init:
                if self.closure_horizontal_cross_hair.get_visible() and \
                        self.closure_vertical_cross_hair.get_visible():
                    self.closure_horizontal_cross_hair.set_visible(False)
                    self.closure_vertical_cross_hair.set_visible(False)
                    self.curr_x = None
                    self.curr_y = None
                    self.draw()


class MainWindow(QMainWindow):
    """
    The main window of our program.
    """
    research_question_label_1: QLabel
    research_question_label_2: QLabel

    plot_navigation_tool_bar: NavigationToolbar
    plot_canvas: PlotCanvas

    global_checkbox: StandardCheckbox
    country_checkbox: StandardCheckbox

    country_selection_label: StandardLabel
    country_selection_combo_box: StandardComboBox

    province_selection_label: StandardLabel
    province_selection_combo_box: StandardComboBox

    city_selection_label: StandardLabel
    city_selection_combo_box: StandardComboBox

    start_date_label: StandardLabel
    end_date_label: StandardLabel
    start_date_edit: StandardDateEdit
    end_date_edit: StandardDateEdit

    confirm_button: StandardPushButton

    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_window()

    def init_window(self) -> None:
        """Initialize the main window"""
        self.resize(1400, 865)

        # Center the window
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

        # Set window title
        self.setWindowTitle('Main Window')

        # Set window icon
        self.setWindowIcon(QIcon('resources/assets/icon.jpg'))

        # Initialize status bar
        self.statusBar().showMessage('Ready.')

        # Initialize Widgets
        self.init_widgets()

        # Initialize Layout
        self.init_layout()

        # Initialize signals (events)
        self.init_signals()

        # Presses the confirm button once when opening the application
        # Renders the plot of the global COVID cases
        self.confirm_button_handler()

    def init_widgets(self) -> None:
        """
        Init all widgets and their attributes.
        """
        # Title (Research Question)
        self.research_question_label_1 = StandardLabel('Educational Crisis - A Closer Examination '
                                                       'on the Correlations Between')
        self.research_question_label_1.set_research_question_font()
        self.research_question_label_1.setAlignment(Qt.AlignBottom)
        self.research_question_label_2 = StandardLabel('Covid - 19 and School Closures Around the Globe')
        self.research_question_label_2.set_research_question_font()
        self.research_question_label_2.setAlignment(Qt.AlignTop)

        # Country selections
        self.country_selection_label = StandardLabel('Country: ')
        self.country_selection_combo_box = StandardComboBox(self)

        self.global_checkbox = StandardCheckbox('Global', self)
        # This setChecked does not trigger the slot because we haven't connected it at this point.
        self.global_checkbox.setChecked(True)
        self.country_checkbox = StandardCheckbox('Country Total', self)

        # Province selection
        self.province_selection_label = StandardLabel('Province: ')
        self.province_selection_combo_box = StandardComboBox(self)

        # City selection
        self.city_selection_label = StandardLabel('City: ')
        self.city_selection_combo_box = StandardComboBox(self)

        # Date selections
        self.start_date_label = StandardLabel('Start Date: ')
        self.end_date_label = StandardLabel('End Date: ')
        self.start_date_edit = StandardDateEdit()
        self.end_date_edit = StandardDateEdit()

        max_date = min(data.ALL_COVID_CASES[-1].date, data.ALL_SCHOOL_CLOSURES[-1].date)
        min_date = max(data.ALL_COVID_CASES[0].date, data.ALL_SCHOOL_CLOSURES[0].date)

        self.start_date_edit.setMinimumDate(min_date)
        self.start_date_edit.setMaximumDate(max_date)
        self.end_date_edit.setMinimumDate(min_date)
        self.end_date_edit.setMaximumDate(max_date)
        self.end_date_edit.setDate(max_date)

        # Plot
        self.plot_canvas = PlotCanvas()
        self.plot_navigation_tool_bar = NavigationToolbar(self.plot_canvas, self)
        set_font(self.plot_navigation_tool_bar)

        # Confirm button
        self.confirm_button = StandardPushButton('Confirm')

    def init_layout(self) -> None:
        """
        Init the layout for all widgets.
        """
        # The main layout of the main window
        main_layout = QVBoxLayout()

        # The layout for our research question
        # I use two lines to show our long title to make it look better
        research_question_layout_1 = QHBoxLayout()
        main_layout.addLayout(research_question_layout_1)
        research_question_layout_1.addStretch(1)
        research_question_layout_1.addWidget(self.research_question_label_1)
        research_question_layout_1.addStretch(1)
        research_question_layout_2 = QHBoxLayout()
        main_layout.addLayout(research_question_layout_2)
        research_question_layout_2.addStretch(1)
        research_question_layout_2.addWidget(self.research_question_label_2)
        research_question_layout_2.addStretch(1)

        # The layout for our options controller
        controller_layout = QHBoxLayout()
        main_layout.addLayout(controller_layout)
        controller_layout.addStretch(1)

        # The layout for our checkbox
        checkbox_layout = QVBoxLayout(self)
        controller_layout.addLayout(checkbox_layout)
        checkbox_layout.addWidget(self.global_checkbox)
        checkbox_layout.addWidget(self.country_checkbox)
        controller_layout.addStretch(1)

        # The layout for country, province, and city selection
        # I comment out the province and city selection because it's useless?
        location_selection_layout = QFormLayout()
        controller_layout.addLayout(location_selection_layout)
        location_selection_layout.addRow(self.country_selection_label,
                                         self.country_selection_combo_box)
        # location_selection_layout.addRow(self.province_selection_label,
        #                                  self.province_selection_combo_box)
        # location_selection_layout.addRow(self.city_selection_label,
        #                                  self.city_selection_combo_box)

        # The layout for date range
        start_date_range_layout = QFormLayout()
        controller_layout.addLayout(start_date_range_layout)
        start_date_range_layout.addRow(self.start_date_label, self.start_date_edit)
        end_date_range_layout = QFormLayout()
        controller_layout.addLayout(end_date_range_layout)
        end_date_range_layout.addRow(self.end_date_label, self.end_date_edit)
        controller_layout.addStretch(3)

        # The confirm button
        main_layout.addWidget(self.confirm_button)

        # The layout for our plot
        plot_layout = QVBoxLayout()
        main_layout.addLayout(plot_layout)
        plot_layout.addWidget(self.plot_navigation_tool_bar)
        plot_layout.addWidget(self.plot_canvas)

        widget = QWidget(self)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def init_signals(self) -> None:
        """
        Init the signals.
        """
        self.global_checkbox.stateChanged.connect(self.on_global_checkbox_changed)
        self.on_global_checkbox_changed(Qt.Checked)
        self.country_checkbox.stateChanged.connect(self.on_country_checkbox_changed)

        self.confirm_button.clicked.connect(self.confirm_button_handler)

        self.country_selection_combo_box.currentIndexChanged.connect(
                self.on_country_selection_changed)
        self.province_selection_combo_box.currentIndexChanged.connect(
                self.on_province_selection_changed)

    @pyqtSlot()
    def confirm_button_handler(self) -> None:
        """
        Things to do when the confirm button is clicked.
        """
        filtered_covid_cases: List[data.CovidCaseData] = []
        filtered_school_closures: List[data.SchoolClosureData] = []

        # Current date range
        q_start_date: QDate = self.start_date_edit.date()
        q_end_date: QDate = self.end_date_edit.date()
        start_date = datetime.date(q_start_date.year(), q_start_date.month(), q_start_date.day())
        end_date = datetime.date(q_end_date.year(), q_end_date.month(), q_end_date.day())

        if self.global_checkbox.isChecked():
            filtered_covid_cases = algorithms.linear_predicate(
                    data.GLOBAL_COVID_CASES, lambda item: start_date <= item.date <= end_date)

            filtered_school_closures = algorithms.linear_predicate(
                    data.GLOBAL_SCHOOL_CLOSURES, lambda item: start_date <= item.date <= end_date)
        else:
            country = data.Country(self.country_selection_combo_box.currentText())

            if self.country_checkbox.isChecked():
                filtered_covid_cases = algorithms.linear_predicate(
                        data.COUNTRIES_TO_COVID_CASES[country],
                        lambda item: start_date <= item.date <= end_date)
            else:
                province = data.Province(self.province_selection_combo_box.currentText(), country)
                city = data.City(self.city_selection_combo_box.currentText(), province)
                filtered_covid_cases = algorithms.linear_predicate(
                        data.COUNTRIES_TO_ALL_COVID_CASES[country],
                        lambda item: (province.name == '' or item.province == province) and
                                     (city.name == '' or item.city == city) and
                                     start_date <= item.date <= end_date)

            filtered_school_closures = algorithms.linear_predicate(
                    data.COUNTRIES_TO_ALL_SCHOOL_CLOSURES[country],
                    lambda item: start_date <= item.date <= end_date
            )

        self.plot_canvas.plot_covid_cases(filtered_covid_cases)
        self.plot_canvas.plot_school_closures(filtered_school_closures)

    @pyqtSlot(int)
    def on_country_selection_changed(self, index: int) -> None:
        """
        Handle things to do after the user selected a country.
        """
        self.province_selection_combo_box.clear()
        self.city_selection_combo_box.clear()

        country = data.SORTED_COUNTRIES[index]

        if country not in data.COUNTRIES_TO_PROVINCES:
            return
        if self.country_checkbox.isChecked():
            return

        provinces = data.COUNTRIES_TO_PROVINCES[country]
        self.province_selection_combo_box.addItems([p.name for p in provinces])

        province = provinces[0]
        if province not in data.PROVINCES_TO_CITIES:
            return

        cities = data.PROVINCES_TO_CITIES[provinces[0]]
        self.city_selection_combo_box.addItems([c.name for c in cities])

    @pyqtSlot(int)
    def on_province_selection_changed(self, index: int) -> None:
        """
        Handle things to do after the user selected a province.
        """
        country = data.SORTED_COUNTRIES[self.country_selection_combo_box.currentIndex()]
        if country not in data.COUNTRIES_TO_PROVINCES:
            return
        provinces = data.COUNTRIES_TO_PROVINCES[country]
        province = provinces[index]

        if province in data.PROVINCES_TO_CITIES:
            cities = data.PROVINCES_TO_CITIES[province]
            self.city_selection_combo_box.clear()
            self.city_selection_combo_box.addItems([c.name for c in cities])

    @pyqtSlot(int)
    def on_global_checkbox_changed(self, state: int) -> None:
        """
        Handle things to do after the user checked or unchecked the global checkbox.
        """
        if state == Qt.Checked:
            self.country_checkbox.setChecked(False)
            self.country_selection_combo_box.clear_and_disable()
            self.province_selection_combo_box.clear_and_disable()
            self.city_selection_combo_box.clear_and_disable()
        else:
            self.set_default_location_selection()

    @pyqtSlot(int)
    def on_country_checkbox_changed(self, state: int) -> None:
        """
        Handle things to do after the user checked or unchecked the country only checkbox.
        """
        if state == Qt.Checked:
            self.global_checkbox.setChecked(False)
            self.province_selection_combo_box.clear_and_disable()
            self.city_selection_combo_box.clear_and_disable()
        else:
            self.province_selection_combo_box.setEnabled(True)
            self.city_selection_combo_box.setEnabled(True)

            country = data.SORTED_COUNTRIES[self.country_selection_combo_box.currentIndex()]

            if country not in data.COUNTRIES_TO_PROVINCES:
                return

            self.province_selection_combo_box.enable_and_add_items(
                    [p.name for p in data.COUNTRIES_TO_PROVINCES[country]])
            province = data.COUNTRIES_TO_PROVINCES[country]
            if province[0] not in data.PROVINCES_TO_CITIES:
                return

            self.city_selection_combo_box.enable_and_add_items(
                    [c.name for c in data.PROVINCES_TO_CITIES[province[0]]])

    def set_default_location_selection(self) -> None:
        """
        Set the location combo box to its default values.

        Default Values:
            - country = Country('Canada')
            - province = Province('Alberta', country)
            - city = None
        """
        self.country_selection_combo_box.clear()
        self.country_selection_combo_box.enable_and_add_items(c.name
                                                              for c in data.SORTED_COUNTRIES)
        default_country = data.Country('Canada')
        self.country_selection_combo_box.setCurrentIndex(
                data.SORTED_COUNTRIES.index(default_country))
        default_provinces = data.COUNTRIES_TO_PROVINCES[default_country]
        self.province_selection_combo_box.clear()
        self.province_selection_combo_box.enable_and_add_items(p.name for p in default_provinces)
        self.city_selection_combo_box.clear()
        self.city_selection_combo_box.setEnabled(True)


# =================================================================================================
# Initialization window.
# =================================================================================================

class DataQThread(QThread):

    def __init__(self, parent=None) -> None:
        super(DataQThread, self).__init__(parent)

    def run(self):
        data.init_data()


class ProgressUpdateThread(QThread):
    on_updated: pyqtSignal = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super(ProgressUpdateThread, self).__init__(parent)

    def run(self) -> None:
        while True:
            progress = data.get_progress()
            self.on_updated.emit(math.floor(progress * 100))
            if progress >= 1:
                self.exit()
                return
            time.sleep(0.1)


class InitWindow(QWidget):
    """
    The window displayed at the initialization phase,
    including a progress bar indicating the percentage of data initialized.
    """
    progress_bar: StandardProgressBar
    progress_bar_update_thread: ProgressUpdateThread

    cancel_button: StandardPushButton

    helper_label: StandardLabel

    sorting_algorithm_combo_box: StandardComboBox
    sorting_algorithm_confirm_button: StandardPushButton

    is_complete: bool = False

    def __init__(self):
        super(InitWindow, self).__init__()
        self.init_window()

    def init_window(self):
        self.resize(800, 200)
        # Center the window
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

        # Set window title
        self.setWindowTitle('Initializing...')

        # Initialize Widgets
        self.init_widgets()

        # Initialize Layout
        self.init_layout()

        # Initialize Signals
        self.init_signals()

        # Start detecting changes in progress
        self.progress_bar_update_thread.start()

    def init_widgets(self):
        self.progress_bar = StandardProgressBar(self)
        self.cancel_button = StandardPushButton('Cancel')
        self.helper_label = StandardLabel(
                'Please select a sorting algorithm for the whole project.\n'
        )
        self.sorting_algorithm_combo_box = StandardComboBox(
                self, items=settings.sort([s for s in algorithms.SORTING_ALGORITHMS],
                                          lambda s1, s2: 1 if s1 > s2 else -1)
        )
        self.sorting_algorithm_confirm_button = StandardPushButton('Confirm')

    def init_layout(self):
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.helper_label)

        algorithms_select_layout = QHBoxLayout(self)
        algorithms_select_layout.addWidget(self.sorting_algorithm_combo_box)
        algorithms_select_layout.addWidget(self.sorting_algorithm_confirm_button)
        main_layout.addLayout(algorithms_select_layout)

        self.setLayout(main_layout)

    def init_signals(self):
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.sorting_algorithm_confirm_button.clicked.connect(self.on_confirm_button_clicked)

        self.progress_bar_update_thread = ProgressUpdateThread()
        self.progress_bar_update_thread.on_updated.connect(self.update_progress_bar)

    @pyqtSlot()
    def on_confirm_button_clicked(self):
        self.helper_label.setText(
                'We have 2,470,748 observations in our data sets and many manipulations, \n'
                'so it may take a bit to load.'
        )
        algorithm_str = self.sorting_algorithm_combo_box.currentText()
        settings.sort = algorithms.SORTING_ALGORITHMS[algorithm_str]
        data_thread = DataQThread(parent=QApplication.instance())
        data_thread.start()

    @pyqtSlot(int)
    def update_progress_bar(self, progress: int) -> None:
        if progress >= 100:
            self.is_complete = True
            self.helper_label.setText('Successfully Loaded! Our main window will appear soon!')
            self.helper_label.adjustSize()
            self.progress_bar.setValue(progress)
            time.sleep(3)
            # This close action will trigger the closeEvent
            self.close()
            # WARNING: We cannot just main_window = MainWindow() because Python's garbage
            # collection will remove it instantly!
            main.main_window = MainWindow()
            main.main_window.show()
        else:
            self.progress_bar.setValue(progress)

    @pyqtSlot()
    def on_cancel_button_clicked(self):
        """
        Handle the things to do after the user clicked the cancel button.
        
        This function will directly interrupt the main thread by raising an exception.
        """
        import _thread
        _thread.interrupt_main()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Handle the things to do after the user press the red close button on the right corner.
        """
        if not self.is_complete:
            import _thread
            _thread.interrupt_main()
        else:
            super(InitWindow, self).closeEvent(a0)
