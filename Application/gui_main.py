"""
This module contains the main window and its elements of our project.

If you are seeing many warnings, that's normal and that's not our fault.
"""
# Python built-ins
import math
import time
from typing import List

# Matplotlib
import matplotlib.backend_bases
import matplotlib.lines
import matplotlib.style
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Our modules
import algorithms
import data
import resource_manager
from gui_utils import *

# Ctype
import ctypes


myappid = 'CSC110.covid_school_plot'  # Random identifier

# Letting Windows display the Icon in the taskbar as well
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

matplotlib.style.use('fast')


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

        # Setting labels and title for COVID Plot
        self.axes_covid.set_title('COVID-19 Cases')
        self.axes_covid.set_xlabel('Dates')
        self.axes_covid.set_ylabel('Cumulative cases')

        # Setting labels and title for Closure Plot
        self.axes_closure.set_title('School Closure Status')
        self.axes_closure.set_xlabel('Dates')

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

        self.axes_closure.set_title('School Closure Status')
        self.axes_closure.set_xlabel('Dates')

        self.draw()
        self.is_closure_cross_hair_init = False

    def on_mouse_move(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """The handler of on_mouse_move event, renders the cross hair"""
        # The reason why the cross-hair is laggy is because self.draw()
        # takes a very long time to draw.
        # This code is a little bit shitty, but we could fix it later.
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


class MainWindowUI(QMainWindow):
    """
    This is the UI of our Main Window with no functionalities.

    Note:
        - We should put, initialize, and layout all widgets needed here.

    Instance Attributes:
        - width: The default width of our window.
        - height: The default height of our window.
        - about_group: The group of widgets decorating and signing our project.
            - big_icon: A big icon on the top left corner of our window, designed by Charlotte.
            - about_label: A label contains our names.
        - initialization_group: A group of widgets who are responsible for initializing our data.
        - location_group: A group of widgets who are responsible for selecting location.
        - date_group: A group of widgets who are responsible for selecting date range.
        - plot_navigation_tool_bar: The matplotlib plot tool bar.
        - plot_canvas: Our customized matplotlib canvas, holding our figures.
        - progress_bar: A progress bar displayed at the right corner of the status bar.
            - It's only responsible for displaying the progress of our data loading process.
    """
    width: int = 1400
    height: int = 865

    # Introduction Group (Decoration)
    about_group: StandardGroupBox
    big_icon: StandardLabel
    about_label: StandardLabel

    # Initialization Group
    initialization_group: StandardGroupBox
    algorithms_selection_label: StandardLabel
    algorithms_selection_combo_box: StandardComboBox
    initialization_helper_label: StandardLabel
    initialization_button: StandardPushButton

    # Location Group
    location_group: StandardGroupBox
    country_search_label: StandardLabel
    country_search_bar: StandardLineEdit
    country_selection_label: StandardLabel
    country_selection_combo_box: StandardComboBox
    global_helper_label: StandardLabel
    global_radio_button: StandardRadioButton
    # Key countries specified by data.KEY_COUNTRIES
    country_shortcut_buttons: List[StandardPushButton]
    location_reset_button: StandardPushButton

    # Date Group
    date_group: StandardGroupBox
    start_date_label: StandardLabel
    end_date_label: StandardLabel
    start_date_edit: StandardDateEdit
    end_date_edit: StandardDateEdit
    start_date_slider: StandardSlider
    end_date_slider: StandardSlider
    date_reset_button: StandardPushButton
    date_confirm_button: StandardPushButton

    # Plot
    plot_navigation_tool_bar: NavigationToolbar
    plot_canvas: PlotCanvas

    # Menu bar
    menu_bar: StandardMenuBar
    file_menu: StandardMenu
    edit_menu: StandardMenu
    help_menu: StandardMenu

    progress_bar: StandardProgressBar

    def __init__(self, *args, **kwargs) -> None:
        """
        Init the whole UI.
        """
        super(MainWindowUI, self).__init__(*args, **kwargs)
        self.init_window()

    def init_window(self) -> None:
        """Init the main window UI"""
        self.resize(self.width, self.height)

        # Center the window
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

        # Set window title
        self.setWindowTitle('Main Window')

        # Set window icon
        icon = QIcon('resources/assets/icon.png')
        self.setWindowIcon(icon)

        # Initialize status bar
        self.statusBar().showMessage('Waiting for initialization start...')

        # Initialize Widgets
        self.init_widgets()

        # Initialize Layout
        self.init_layout()

    def init_widgets(self) -> None:
        """
        Init all widgets and their attributes.
        """
        # Introduction Group
        self.about_group = StandardGroupBox('About', self)
        self.big_icon = StandardLabel(parent=self.about_group)
        pixmap = QPixmap(
                resource_manager.RESOURCES_DICT[resource_manager.ICON_RESOURCE_NAME].local_path) \
            .scaled(120, 120, Qt.KeepAspectRatio)
        self.big_icon.setPixmap(pixmap)
        self.about_label = StandardLabel('By Alyssa, \nCharlotte, \nRay, and \nScott',
                                         self.about_group)
        self.about_label.setAlignment(Qt.AlignCenter)

        # Initialization Group
        self.initialization_group = StandardGroupBox('Initialization', self)
        self.algorithms_selection_label = StandardLabel('Select a sorting algorithm',
                                                        self.initialization_group)
        self.algorithms_selection_combo_box = \
            StandardComboBox(self.initialization_group, algorithms.SORTING_ALGORITHMS.keys())
        self.initialization_helper_label = StandardLabel(
                'Please click the button below \nto initialize our data!'
        )
        self.initialization_button = StandardPushButton('Initialize', self.initialization_group)

        # Location Group
        self.location_group = StandardGroupBox('Location', self)
        self.country_search_label = StandardLabel('Search', self.location_group)
        self.country_search_bar = StandardLineEdit(parent=self.location_group)
        self.country_selection_label = StandardLabel('Country', self.location_group)
        self.country_selection_combo_box = StandardComboBox(self.location_group)
        self.global_helper_label = StandardLabel('Global View')
        self.global_radio_button = StandardRadioButton('Global', self.location_group)
        self.country_shortcut_buttons = [StandardPushButton(c.name, self.location_group)
                                         for c in data.KEY_COUNTRIES]
        self.location_reset_button = StandardPushButton('Reset', self.location_group)

        # Date Group
        self.date_group = StandardGroupBox('Date', self)
        self.start_date_label = StandardLabel('Start Date: ', self.date_group)
        self.end_date_label = StandardLabel('End Date: ', self.date_group)
        self.start_date_edit = StandardDateEdit(self.date_group)
        self.end_date_edit = StandardDateEdit(self.date_group)
        self.start_date_slider = StandardSlider(parent=self.date_group)
        self.end_date_slider = StandardSlider(parent=self.date_group)
        self.date_reset_button = StandardPushButton('Reset', self.date_group)
        self.date_confirm_button = StandardPushButton('Confirm', self.date_group)

        # Plot
        self.plot_canvas = PlotCanvas()
        self.plot_navigation_tool_bar = StandardNavigationToolbar(self.plot_canvas, self)
        set_font(self.plot_navigation_tool_bar)

        # Progress bar on status bar
        self.progress_bar = StandardProgressBar(self.statusBar())
        self.progress_bar.setValue(0)
        set_font(self.progress_bar, font_size=10)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

        # Menu bar
        self.menu_bar = StandardMenuBar(self)
        self.file_menu = self.menu_bar.addMenu('File')
        self.edit_menu = self.menu_bar.addMenu('Edit')
        self.help_menu = self.menu_bar.addMenu('Help')

        self.setMenuBar(self.menu_bar)

    def init_layout(self) -> None:
        """
        Init the layout for all widgets.
        """
        widget = QWidget(self)
        # The main layout of the main window
        main_layout = QVBoxLayout(widget)

        controller_layout = QHBoxLayout(widget)

        # Controller Layout Group
        main_layout.addLayout(controller_layout, 382)

        # Introduction Group
        controller_layout.addWidget(self.about_group)
        introduction_group_layout = QVBoxLayout(self.about_group)
        introduction_group_layout.addWidget(self.big_icon)
        introduction_group_layout.addWidget(self.about_label, alignment=Qt.AlignCenter)

        # Initialization Group
        controller_layout.addWidget(self.initialization_group)
        initialization_group_layout = QVBoxLayout(self.initialization_group)
        initialization_group_layout.addWidget(self.algorithms_selection_label, 1)
        initialization_group_layout.addWidget(self.algorithms_selection_combo_box, 2)
        initialization_group_layout.addWidget(self.initialization_helper_label, 2)
        initialization_group_layout.addWidget(self.initialization_button, 2)

        # Location Group
        controller_layout.addWidget(self.location_group)
        location_group_layout = QGridLayout(self.location_group)
        location_group_layout.addWidget(self.country_search_label, 0, 0)
        location_group_layout.addWidget(self.country_search_bar, 0, 1)
        location_group_layout.addWidget(self.global_helper_label, 0, 2)
        location_group_layout.addWidget(self.country_selection_label, 1, 0)
        location_group_layout.addWidget(self.country_selection_combo_box, 1, 1)
        location_group_layout.addWidget(self.global_radio_button, 1, 2)
        index: int = 0
        for row in range(2, 5):
            for column in range(2):
                location_group_layout.addWidget(self.country_shortcut_buttons[index], row, column)
                index += 1
        location_group_layout.addWidget(self.location_reset_button, 4, 2)

        # Date Group
        controller_layout.addWidget(self.date_group)
        date_group_layout = QGridLayout(self.date_group)
        date_group_layout.addWidget(self.start_date_label, 0, 0)
        date_group_layout.addWidget(self.start_date_edit, 1, 0)
        date_group_layout.addWidget(self.start_date_slider, 1, 1)
        date_group_layout.addWidget(self.end_date_label, 2, 0)
        date_group_layout.addWidget(self.end_date_edit, 3, 0)
        date_group_layout.addWidget(self.end_date_slider, 3, 1)
        date_group_layout.addWidget(self.date_reset_button, 4, 0, 2, 1)
        date_group_layout.addWidget(self.date_confirm_button, 4, 1, 2, 1)

        plot_layout = QVBoxLayout()
        main_layout.addLayout(plot_layout, 618)
        plot_layout.addWidget(self.plot_navigation_tool_bar)
        plot_layout.addWidget(self.plot_canvas)

        widget.setLayout(main_layout)
        self.setCentralWidget(widget)


class DataThread(QThread):
    """
    A QThread subclass that initializes our data asynchronously.
    """

    def __init__(self, parent: QObject) -> None:
        super(DataThread, self).__init__(parent)

    def run(self):
        data.init_data()


class ProgressUpdateThread(QThread):
    """
    A QThread subclass that monitors the progress of data initialization (when applicable) and
    emits the progress and progress description to the main thread (main window).

    We used PyQt signal and slot mechanism to achieve that.
    """
    on_updated: pyqtSignal = pyqtSignal(int, str)

    def __init__(self, parent: QObject) -> None:
        super(ProgressUpdateThread, self).__init__(parent)

    def run(self) -> None:
        while True:
            progress, description = data.get_progress()
            self.on_updated.emit(math.floor(progress * 100), description)
            # If the description contains Failed to, meaning that some critical errors happened.
            # This could be improved but it's not worthy for our purposes.
            if progress >= 1 or 'Failed to' in description:
                self.exit()
                return
            time.sleep(0.05)


class MainWindow(MainWindowUI):
    """
    The main window of our program.

    Instance Attributes:
        - progress_bar_update_thread: The thread for monitoring the progress of data init.
        - is_user_change_date: True if the user is editing the date.
            - The reason we used it here is that sometimes we need to change the date
              programmatically, but we don't want the slot to be signaled when we change the date
              programmatically.
    """
    progress_bar_update_thread: ProgressUpdateThread

    is_user_operation: bool = True

    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        # Please ignore the warning here.
        self.progress_bar_update_thread = ProgressUpdateThread(self)

        # Initialize menu
        self.init_menu()

        # Initialize signals
        self.init_signals()

        # Now, our data haven't initialized yet, so we disable all functional widgets for safety.
        self.set_enabled_functional_widgets(False)

    def init_menu(self) -> None:
        """
        Initialize the menu bar
        """
        save_plot = QAction('Save current plot', self)
        save_plot.setShortcut('Ctrl+S')
        save_plot.triggered.connect(self.save_plot)

        self.file_menu.addAction(save_plot)

        exit_action = QAction('Exit App', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exit)

        self.file_menu.addAction(exit_action)


    def init_signals(self) -> None:
        """
        Init the signals.
        """
        # Progress bar update
        self.progress_bar_update_thread.on_updated.connect(self.update_progress_bar)
        # Init button
        self.initialization_button.clicked.connect(self.on_init_button_clicked)
        # Country selection
        self.country_search_bar.textEdited.connect(self.on_country_search_bar_edited)
        self.country_selection_combo_box.currentTextChanged.connect(
                self.on_country_selection_combo_box_changed)
        # Global radio button
        self.global_radio_button.toggled.connect(self.on_global_radio_button_toggled)
        for button in self.country_shortcut_buttons:
            button.clicked.connect(self.on_country_shortcut_buttons_clicked)
        # Location reset button
        self.location_reset_button.clicked.connect(self.on_location_reset_button_clicked)
        # Date confirm button
        self.date_confirm_button.clicked.connect(self.on_date_confirm_button_clicked)
        # Date reset button
        self.date_reset_button.clicked.connect(self.on_date_reset_button_clicked)
        # Date edit
        self.start_date_edit.dateChanged.connect(self.on_start_date_edit_changed)
        self.end_date_edit.dateChanged.connect(self.on_end_date_edit_changed)
        # Date slider
        self.start_date_slider.sliderMoved.connect(self.on_start_date_slider_moved)
        self.end_date_slider.sliderMoved.connect(self.on_end_date_slider_moved)

    def update_plot(self) -> None:
        """
        Update the plot according to current location and date range.

        Note:
            - Due to matplotlib, this function is actually not very efficient, so pls use it only
              when necessary.
        """
        filtered_covid_cases: List[data.CovidCaseData]
        filtered_school_closures: List[data.SchoolClosureData]

        # Current date range
        start_date: QDate = self.start_date_edit.date().toPyDate()
        end_date: QDate = self.end_date_edit.date().toPyDate()

        if self.global_radio_button.isChecked():
            filtered_covid_cases = algorithms.linear_predicate(
                    data.GLOBAL_COVID_CASES, lambda c: start_date <= c.date <= end_date)
            filtered_school_closures = algorithms.linear_predicate(
                    data.GLOBAL_SCHOOL_CLOSURES, lambda c: start_date <= c.date <= end_date)
        else:
            country = data.Country(self.country_selection_combo_box.currentText())
            filtered_covid_cases = algorithms.linear_predicate(
                    data.COUNTRIES_TO_COVID_CASES[country],
                    lambda c: start_date <= c.date <= end_date)
            filtered_school_closures = algorithms.linear_predicate(
                    data.COUNTRIES_TO_SCHOOL_CLOSURES[country],
                    lambda c: start_date <= c.date <= end_date)

        self.plot_canvas.plot_covid_cases(filtered_covid_cases)
        self.plot_canvas.plot_school_closures(filtered_school_closures)

    def set_enabled_functional_widgets(self, is_enable: bool) -> None:
        """
        Enable or disable the functional widgets:
            - location_group
            - date_group
            - plot_canvas
        """
        self.location_group.setEnabled(is_enable)
        self.date_group.setEnabled(is_enable)
        self.plot_canvas.setEnabled(is_enable)

    def init_content(self) -> None:
        """
        Initialize those functional widgets.

        Note:
            - This function should only be called after data are initialized.
        """
        if not self.global_radio_button.isChecked():
            self.global_radio_button.toggle()
        # Location
        self.set_default_location()
        # Date
        self.set_default_date()

    def set_default_location(self) -> None:
        """
        Set the location group to its default state.
        Our default country is Canada.

        Note:
            - This function should only be called after data are initialized.
        """
        if not self.global_radio_button.isChecked():
            self.global_radio_button.toggle()
        self.country_selection_combo_box.clear()
        self.country_selection_combo_box.addItems([c.name for c in data.SORTED_COUNTRIES])
        self.country_selection_combo_box.setCurrentText('Canada')

    def set_default_date(self) -> None:
        """
        Set the date group to its default state.

        Note:
            - This function should only be called after data are initialized.
        """
        max_date = min(data.ALL_COVID_CASES[-1].date, data.ALL_SCHOOL_CLOSURES[-1].date)
        min_date = max(data.ALL_COVID_CASES[0].date, data.ALL_SCHOOL_CLOSURES[0].date)
        self.end_date_edit.set_extremum_date(min_date, max_date)
        self.end_date_edit.setDate(max_date)
        self.start_date_edit.set_extremum_date(min_date, max_date)
        self.start_date_edit.setDate(min_date)

    @pyqtSlot(int, str)
    def update_progress_bar(self, progress: int, description: str) -> None:
        """
        Update the progress bar and progress description (on status bar).
        If data are initialized (progress >= 100), then we init our contents and hide the
        progress bar.
        """
        if 'Failed to' in description:
            # TODO Add instructions
            QMessageBox.critical(self, 'Critical', f'{description} \n Please ...',
                                 QMessageBox.Ok, QMessageBox.Ok)
            QApplication.quit()

        self.progress_bar.setValue(progress)
        self.statusBar().showMessage(description)
        if progress >= 100:
            self.init_content()
            self.set_enabled_functional_widgets(True)
            self.progress_bar.setVisible(False)
            self.update_plot()
            self.initialization_helper_label.setText('Please click the button below \nto reinitialize our data!')

    @pyqtSlot()
    def on_init_button_clicked(self) -> None:
        """
        We initialize or re-initialize our data when the initialized_button is clicked.
        """
        if not self.progress_bar_update_thread.isRunning():
            self.set_enabled_functional_widgets(False)
            data.reset_data()
            settings.sort = \
                algorithms.SORTING_ALGORITHMS[self.algorithms_selection_combo_box.currentText()]
            self.progress_bar.setVisible(True)
            self.progress_bar_update_thread.start()
            # Please ignore the warning here.
            data_thread = DataThread(self)
            data_thread.start()

    @pyqtSlot(str)
    def on_country_search_bar_edited(self, new_text: str) -> None:
        """
        When the texts in the search bar are edited by users, then we update the current country
        respectively.
        """
        if self.global_radio_button.isChecked():
            self.global_radio_button.toggle()
        country_name = 'Canada'
        if new_text == '':
            return
        new_text = new_text.lower()
        for country in data.SORTED_COUNTRIES:
            if new_text in country.name.lower():
                country_name = country.name
                break
        self.country_selection_combo_box.setCurrentText(country_name)

    @pyqtSlot(bool)
    def on_global_radio_button_toggled(self, is_checked: bool) -> None:
        """
        If the global_radio_button is checked, then we uncheck it and enable our country selection.
        """
        self.country_selection_combo_box.setEnabled(not is_checked)
        self.update_plot()

    @pyqtSlot()
    def on_country_selection_combo_box_changed(self) -> None:
        self.update_plot()

    @pyqtSlot()
    def on_country_shortcut_buttons_clicked(self) -> None:
        # This could actually get the sender button.
        button = self.sender()
        country_name = button.text()
        self.country_selection_combo_box.setCurrentText(country_name)
        self.global_radio_button.setChecked(False)

    @pyqtSlot()
    def on_location_reset_button_clicked(self) -> None:
        self.set_default_location()
        self.update_plot()

    @pyqtSlot()
    def on_date_confirm_button_clicked(self) -> None:
        self.update_plot()

    @pyqtSlot()
    def on_date_reset_button_clicked(self) -> None:
        self.set_default_date()
        self.update_plot()

    def on_date_edit_changed(self, new_date: QDate, date_slider: StandardSlider) -> None:
        """
        When the date is edited by users, we update the tick of the slider to the correct position.
        """
        if not self.is_user_operation:
            return
        new_date = new_date.toPyDate()
        min_date = self.start_date_edit.minimumDate().toPyDate()
        max_date = self.end_date_edit.maximumDate().toPyDate()
        delta1 = new_date - min_date
        delta2 = max_date - min_date
        date_slider.setValue(math.ceil((delta1 / delta2) * 100))

    @pyqtSlot(QDate)
    def on_start_date_edit_changed(self, new_date: QDate) -> None:
        max_qdate = self.end_date_edit.date()
        max_date = max_qdate.toPyDate()
        if new_date.toPyDate() > max_date:
            QMessageBox.warning(self, 'Warning', 'End date should not be smaller than start date!',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.start_date_edit.setDate(max_qdate)
            self.on_date_edit_changed(max_qdate, self.start_date_slider)
        else:
            self.on_date_edit_changed(new_date, self.start_date_slider)

    @pyqtSlot(QDate)
    def on_end_date_edit_changed(self, new_date: QDate) -> None:
        min_qdate = self.start_date_edit.date()
        min_date = min_qdate.toPyDate()
        if new_date.toPyDate() < min_date:
            QMessageBox.warning(self, 'Warning', 'End date should not be smaller than start date!',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.end_date_edit.setDate(min_qdate)
            self.on_date_edit_changed(min_qdate, self.end_date_slider)
        else:
            self.on_date_edit_changed(new_date, self.end_date_slider)

    def on_slider_moved(self, percentage: float, date_edit: StandardDateEdit) -> None:
        """
        When users move the slider, we update the date_edit to display the correct date.
        """
        min_date = self.start_date_edit.minimumDate().toPyDate()
        max_date = self.end_date_edit.maximumDate().toPyDate()
        delta = max_date - min_date
        delta *= percentage
        self.is_user_operation = False
        date_edit.setDate(min_date + delta)
        self.is_user_operation = True

    @pyqtSlot(int)
    def on_start_date_slider_moved(self, new_value: int) -> None:
        if new_value > self.end_date_slider.value():
            self.start_date_slider.setValue(new_value - 1)
            return
        percentage = new_value / self.start_date_slider.maximum()
        self.on_slider_moved(percentage, self.start_date_edit)

    @pyqtSlot(int)
    def on_end_date_slider_moved(self, new_value: int) -> None:
        if new_value < self.start_date_slider.value():
            self.end_date_slider.setValue(new_value + 1)
            return
        percentage = new_value / self.end_date_slider.maximum()
        self.on_slider_moved(percentage, self.end_date_edit)

    def save_plot(self) -> None:
        """Saves the current plots at the specified location"""
        # The second return value is "Selected filter", which is useless
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png)")

        if path == '':
            # This is because the user may press cancel
            return

        # Saving canvas at desired path
        self.plot_canvas.print_png(path)

    def exit(self) -> None:
        """Closes the application the moment when triggered"""
        QApplication.quit()


