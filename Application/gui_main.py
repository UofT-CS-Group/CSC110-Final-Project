"""
This module contains the main window and its elements of our project.

If you are seeing many warnings, that's normal and that's not our fault.
"""
# Python built-ins
import math
import time
from typing import Any, List, Tuple

# Matplotlib
import matplotlib.backend_bases
import matplotlib.lines
import matplotlib.style
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Our modules
import algorithms
import data
import resource_manager
from gui_utils import *

matplotlib.style.use('fast')


class PlotToolbar(NavigationToolbar):
    """
    A standard menu for our project.
    When needed, we could add more attributes and methods.
    """

    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in {'Home'}]
    window: Any

    def __init__(self, canvas, parent, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        self.window = parent
        set_font(self)

    def _init_toolbar(self):
        """
        Just leave it as blank.
        """
        pass

    def home(self, *args):
        self.window.update_plot()


class PlotCanvas(FigureCanvas):
    """
    Figure widget from matplotlib with a cross-hair.
    """
    figure: pyplot.Figure
    covid_axes: pyplot.Axes
    closure_axes: pyplot.Axes
    background: Any

    covid_x_data: List[datetime.date]
    covid_y_data: List[int]

    closure_x_data: List[datetime.date]
    closure_y_data: List[int]

    covid_horizontal_cross_hair: matplotlib.lines.Line2D
    covid_vertical_cross_hair: matplotlib.lines.Line2D
    closure_horizontal_cross_hair: matplotlib.lines.Line2D
    closure_vertical_cross_hair: matplotlib.lines.Line2D

    covid_prev_x: float = 0
    covid_prev_y: float = 0
    closure_prev_x: float = 0
    closure_prev_y: float = 0

    def __init__(self) -> None:
        self.figure = pyplot.Figure(tight_layout=True, linewidth=1)
        super(PlotCanvas, self).__init__(self.figure)

        self.covid_axes, self.closure_axes = self.figure.subplots(1, 2)
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('scroll_event', self.on_scroll)
        self.mpl_connect('button_press_event', self.on_mouse_button_press)
        self.mpl_connect('button_release_event', self.on_mouse_button_release)

        self.init_figures()
        # Initialize curr_x and curr_y to None and updated from the on_mouse_move function
        self.curr_x = None
        self.curr_y = None
        # Formatting the right upper corner of the display
        self.covid_axes.format_coord = lambda _, __: \
            f'Date = {self.curr_x}, Cases = {self.curr_y}'
        self.closure_axes.format_coord = lambda _, __: \
            f'Date = {self.curr_x}, Status = ' \
            f'{data.ENUM_TO_STATUS_DICT[data.ClosureStatus(self.curr_y)]}'

        self.draw()

        self.covid_horizontal_cross_hair = self.covid_axes.axhline(
                y=0, color='black', linewidth=0.8, linestyle='--', animated=True)
        self.covid_vertical_cross_hair = self.covid_axes.axvline(
                x=0, color='black', linewidth=0.8, linestyle='--', animated=True)
        self.closure_horizontal_cross_hair = self.closure_axes.axhline(
                y=0, color='black', linewidth=0.8, linestyle='--', animated=True)
        self.closure_vertical_cross_hair = self.closure_axes.axvline(
                x=0, color='black', linewidth=0.8, linestyle='--', animated=True)

    def init_figures(self) -> None:
        # Setting labels and title
        self.covid_axes.set_title('COVID-19 Cases')
        self.covid_axes.set_xlabel('Dates')
        self.covid_axes.set_ylabel('Cumulative cases')

        self.closure_axes.set_yticks(ticks=[0, 1, 2, 3], minor=False)
        self.closure_axes.set_yticklabels(
                labels=['Academic Break', 'Fully Open', 'Partially Open', 'Closed'],
                minor=False)

        for text in self.covid_axes.get_xticklabels():
            text.set_rotation(40.0)
        for text in self.closure_axes.get_xticklabels():
            text.set_rotation(40.0)

        self.closure_axes.set_title('School Closure Status')
        self.closure_axes.set_xlabel('Dates')

    def update_background(self):
        self.background = self.copy_from_bbox(self.figure.bbox)

    def plot_covid_cases(self, covid_cases: List[data.CovidCaseData]) -> None:
        """Plots the COVID Data in self.axes_covid"""
        self.covid_x_data = [c.date for c in covid_cases]
        self.covid_y_data = [c.cases for c in covid_cases]

        self.covid_axes.clear()
        self.init_figures()
        self.covid_axes.plot(self.covid_x_data, self.covid_y_data, marker='.', color='orange')

        self.draw()
        self.update_background()

    def plot_school_closures(self, school_closures: List[data.SchoolClosureData]) -> None:
        """Plots the Closure Data in self.axes_closure"""
        self.closure_x_data = [c.date for c in school_closures]
        self.closure_y_data = [c.status.value for c in school_closures]

        self.closure_axes.clear()
        self.init_figures()
        self.closure_axes.plot(self.closure_x_data, self.closure_y_data, marker='.', color='green')

        self.draw()
        self.update_background()

    def get_closet_coordinates_from_x(self, x: int, x_data: List, y_data: List) -> Tuple[int, int]:
        x_date = datetime.date.fromtimestamp(0) + datetime.timedelta(days=x)
        index = algorithms.binary_search(x_data, x_date)
        x = (x_data[index] - datetime.date.fromtimestamp(0)).days
        y = y_data[min(index + 1, len(y_data) - 1)]
        self.curr_x = x_date
        self.curr_y = y
        return x, y

    def pan(self, axes: pyplot.Axes, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Pan the axes based on the given mouse event.
        """
        min_x, max_x = axes.get_xlim()
        min_y, max_y = axes.get_ylim()
        display_to_data = axes.transData.inverted()
        prev_data = (0, 0)

        if axes is self.covid_axes:
            prev_data = display_to_data.transform_point((self.covid_prev_x, self.covid_prev_y))
            self.covid_prev_x = event.x
            self.covid_prev_y = event.y
        elif axes is self.closure_axes:
            prev_data = display_to_data.transform_point((self.closure_prev_x, self.closure_prev_y))
            self.closure_prev_x = event.x
            self.closure_prev_y = event.y

        dx = (event.xdata - prev_data[0])
        dy = (event.ydata - prev_data[1])

        axes.set_xlim(min_x - dx, max_x - dx)
        axes.set_ylim(min_y - dy, max_y - dy)

        self.draw()
        self.update_background()

    def on_mouse_move(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        The handler of on_mouse_move event, which renders the cross-hair and mouse drag (pan).
        Optimized with blit, so now the FPS is very high.
        """
        self.restore_region(self.background)
        if not event.inaxes:
            self.covid_horizontal_cross_hair.set_visible(False)
            self.covid_vertical_cross_hair.set_visible(False)
            self.closure_horizontal_cross_hair.set_visible(False)
            self.closure_vertical_cross_hair.set_visible(False)
            self.curr_x = None
            self.curr_y = None
            return

        x = event.xdata
        y = event.ydata

        if event.inaxes is self.covid_axes:
            if event.button == matplotlib.backend_bases.MouseButton.LEFT:
                self.pan(self.covid_axes, event)

            x, y = self.get_closet_coordinates_from_x(
                    x, self.covid_x_data, self.covid_y_data)

            self.covid_horizontal_cross_hair.set_visible(True)
            self.covid_vertical_cross_hair.set_visible(True)
            self.covid_horizontal_cross_hair.set_ydata(y)
            self.covid_vertical_cross_hair.set_xdata(x)
            self.covid_axes.draw_artist(self.covid_horizontal_cross_hair)
            self.covid_axes.draw_artist(self.covid_vertical_cross_hair)

        elif event.inaxes is self.closure_axes:
            if event.button == matplotlib.backend_bases.MouseButton.LEFT:
                self.pan(self.closure_axes, event)

            x, y = self.get_closet_coordinates_from_x(
                    x, self.closure_x_data, self.closure_y_data)

            self.closure_horizontal_cross_hair.set_visible(True)
            self.closure_vertical_cross_hair.set_visible(True)
            self.closure_horizontal_cross_hair.set_ydata(y)
            self.closure_vertical_cross_hair.set_xdata(x)
            self.closure_axes.draw_artist(self.closure_horizontal_cross_hair)
            self.closure_axes.draw_artist(self.closure_vertical_cross_hair)

        self.blit(self.figure.bbox)
        self.flush_events()

    @staticmethod
    def zoom(is_zoom_in: bool, zoom_factor: float, x: float,
             original_min: float, original_max: float) -> Tuple[float, float]:
        length = original_max - original_min
        zoom_length = length * zoom_factor
        left_ratio = (x - original_min) / length
        right_ratio = 1 - left_ratio
        left_zoom_length = zoom_length * left_ratio
        right_zoom_length = zoom_length * right_ratio

        if is_zoom_in:
            return original_min + left_zoom_length, original_max - right_zoom_length
        else:
            return original_min - left_zoom_length, original_max + right_zoom_length

    def on_scroll(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """
        Zoom in or zoom out.
        """
        if not event.inaxes:
            return

        zoom_factor = 0.2
        x = event.xdata
        y = event.ydata
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0

        if event.inaxes is self.covid_axes:
            min_x, max_x = self.covid_axes.get_xlim()
            min_y, max_y = self.covid_axes.get_ylim()
        elif event.inaxes is self.closure_axes:
            min_x, max_x = self.closure_axes.get_xlim()
            min_y, max_y = self.closure_axes.get_ylim()

        if event.button == 'up':
            min_x, max_x = self.zoom(True, zoom_factor, x, min_x, max_x)
            min_y, max_y = self.zoom(True, zoom_factor, y, min_y, max_y)
        elif event.button == 'down':
            min_x, max_x = self.zoom(False, zoom_factor, x, min_x, max_x)
            min_y, max_y = self.zoom(False, zoom_factor, y, min_y, max_y)

        if event.inaxes is self.covid_axes:
            self.covid_axes.set_xlim(min_x, max_x)
            self.covid_axes.set_ylim(min_y, max_y)
        elif event.inaxes is self.closure_axes:
            self.closure_axes.set_xlim(min_x, max_x)

        self.draw()
        self.update_background()

    def on_mouse_button_press(self, event: matplotlib.backend_bases.MouseEvent):
        if event.button == matplotlib.backend_bases.MouseButton.LEFT:
            if event.inaxes is self.covid_axes:
                self.covid_prev_x = event.x
                self.covid_prev_y = event.y
                self.closure_prev_x = 0
                self.closure_prev_y = 0
            elif event.inaxes is self.closure_axes:
                self.covid_prev_x = 0
                self.covid_prev_y = 0
                self.closure_prev_x = event.x
                self.closure_prev_y = event.y

    def on_mouse_button_release(self, event: matplotlib.backend_bases.MouseEvent):
        self.covid_prev_x = 0
        self.covid_prev_y = 0
        self.closure_prev_x = 0
        self.closure_prev_y = 0


class MainWindowUI(QMainWindow):
    """
    This is the UI of our Main Window with no functionalities.

    Note:
        - We should put, initialize, and layout all widgets needed here.

    Instance Attributes:
        - width: The default width of our window.
        - height: The default height of our window.
        - about_group: The group of widgets decorating and signing our project.
            - big_icon: A big icon in the top left corner of our window, designed by Charlotte.
            - about_label: A label contains our names.
        - initialization_group: A group of widgets who are responsible for initializing our data.
        - location_group: A group of widgets who are responsible for selecting location.
        - date_group: A group of widgets who are responsible for selecting date range.
        - plot_navigation_tool_bar: The matplotlib plot toolbar.
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
    plot_tool_bar: PlotToolbar
    plot_canvas: PlotCanvas

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
        self.algorithms_selection_label = StandardLabel('Select a sorting algorithms:',
                                                        self.initialization_group)
        self.algorithms_selection_combo_box = \
            StandardComboBox(self.initialization_group, algorithms.SORTING_ALGORITHMS.keys())
        self.initialization_helper_label = StandardLabel(
                'Please click the button \nto start initializing our data!'
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
        self.plot_tool_bar = PlotToolbar(self.plot_canvas, self)

        # Progress bar on status bar
        self.progress_bar = StandardProgressBar(self.statusBar())
        self.progress_bar.setValue(0)
        set_font(self.progress_bar, font_size=10)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)

    def init_layout(self) -> None:
        """
        Init the layout for all widgets.
        """
        widget = QWidget(self)
        # The main layout of the main window
        main_layout = QVBoxLayout(widget)

        controller_layout = QHBoxLayout(widget)
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
        plot_layout.addWidget(self.plot_tool_bar)
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
            # This could be improved, but it's not worthy for our purposes.
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

        # Initialize signals
        self.init_signals()

        # Now, our data haven't initialized yet, so we disable all functional widgets for safety.
        self.set_enabled_functional_widgets(False)

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
        If data are initialized (progress >= 100), then we initialize our contents and hide the
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
