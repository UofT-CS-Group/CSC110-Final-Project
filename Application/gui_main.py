"""
This module contains the main window and its elements of our project.

If you are seeing many warnings, that's normal and that's not our fault.
"""
# Python built-ins
import math
import platform
import time
from typing import Any, List, Tuple

# Matplotlib
import matplotlib.axes
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

if platform.system() == 'Windows':
    # Ctype
    import ctypes

    app_id = 'CSC110.covid_school_plot'  # Random identifier
    # Letting Windows display the Icon in the taskbar as well
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

matplotlib.style.use('fast')


class PlotToolbar(NavigationToolbar):
    """
    A customized toolbar from matplotlib.

    When needed, we could add more attributes and methods.

    Instance Attributes:
        - toolitems: Override the super toolitems for our purpose.
        - window: A MainWindow instance that is the parent window of this toolbar.
    """

    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in {'Home'}]
    window: Any

    def __init__(self, canvas, parent, coordinates=True) -> None:
        super().__init__(canvas, parent, coordinates)
        self.window = parent
        set_font(self)

    def _init_toolbar(self) -> None:
        """
        Just leave it as blank.
        """
        pass

    def home(self, *args) -> None:
        """
        Override the super home function.

        This function is executed when user clicks the home button on this toolbar.
        If user clicked it, then we replot our plots to its original states.
        """
        if self.canvas.plotted:
            self.window.update_plot()


class PlotCanvas(FigureCanvas):
    """
    Figure widget from matplotlib with many customizations like cross-hair, customized zoom,
    and pan.

    We used blit to optimize the frame rates of the figure.

    Instance Attributes:
        - figure: The actual matplotlib figure instance.
        - covid_axes: The axes of covid cases plot.
        - closure_axes: The axes of closure status plot.
        - background: The background of the figure, and it's used for blitting.
        - curr_x: Current x value that should always be a date.
        - curr_y: Current y value that should always be an int.
            - Note: curr_x and curr_y may be None if the cursor is not on the axes.
        - covid_line_color and closure_line_color: The line color of covid_axes and closure_axes.
        - covid_line_style and closure_line_style: The line style of covid_axes and closure_axes.
        - covid_data_marker and closure_data_marker: The line marker of covid_axes and closure_axes.
        - covid_x_data and closure_x_data: The current data of the x-axis.
        - covid_y_data and closure_y_data: The current data of the y-axis.
        - covid_horizontal_cross_hair and ...: The cross-hairs.
        - covid_prev_x and ...: The previous cursor positions (in pixel, not real data).
    """
    figure: pyplot.Figure
    covid_axes: pyplot.Axes
    closure_axes: pyplot.Axes
    background: Any

    curr_x: Optional[datetime.date]
    curr_y: Optional[int]

    covid_line_color: str = '#ff557f'
    closure_line_color: str = '#55ff7f'

    covid_line_style: str = 'solid'
    closure_line_style: str = 'solid'

    covid_data_marker: str = '.'
    closure_data_marker: str = '.'

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

    plotted: bool

    def __init__(self) -> None:
        """
        Initialize a PlotCanvas instance.
        It will create figures and axes, connect events, and other necessary works.
        """
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

        # Initialize a storage bool to check if the plots are out
        self.plotted = False

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
        """
        Initialize the matplotlib figure, including titles and labels.
        """
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
        """
        Update self.background.
        Note:
            - This function should be called everytime after a call to self.draw().
            - Because we need to update any changes of the background of the plot after redrawing.
        """
        self.background = self.copy_from_bbox(self.figure.bbox)

    def update_lines(self, axes: matplotlib.axes.Axes,
                     color: Optional[str] = None,
                     style: Optional[str] = None,
                     marker: Optional[str] = None):
        """
        Update the color, style, and marker of lines in the given axes.
        """
        if axes is self.covid_axes:
            if color is not None:
                self.covid_line_color = color
            if style is not None:
                self.covid_line_style = style
            if marker is not None:
                self.covid_data_marker = marker
        elif axes is self.closure_axes:
            if color is not None:
                self.closure_line_color = color
            if style is not None:
                self.closure_line_style = style
            if marker is not None:
                self.closure_data_marker = marker
        else:
            raise ValueError('Illegal Axes!')

        for line in axes.get_lines():
            line: matplotlib.lines.Line2D

            if color is not None:
                line.set_color(color)
            if style is not None:
                line.set_linestyle(style)
            if marker is not None:
                line.set_marker(marker)

        self.draw()
        self.update_background()

    def plot_covid_cases(self, covid_cases: List[data.CovidCaseData]) -> None:
        """Plots covid_cases in self.axes_covid"""
        self.covid_x_data = [c.date for c in covid_cases]
        self.covid_y_data = [c.cases for c in covid_cases]

        self.covid_axes.clear()
        self.init_figures()
        self.covid_axes.plot(self.covid_x_data, self.covid_y_data,
                             linestyle=self.covid_line_style,
                             marker=self.covid_data_marker,
                             color=self.covid_line_color)

        self.draw()
        self.update_background()

    def plot_school_closures(self, school_closures: List[data.SchoolClosureData]) -> None:
        """Plots school_closures in self.axes_closure"""
        self.closure_x_data = [c.date for c in school_closures]
        self.closure_y_data = [c.status.value for c in school_closures]

        self.closure_axes.clear()
        self.init_figures()
        self.closure_axes.plot(self.closure_x_data, self.closure_y_data,
                               linestyle=self.closure_line_style,
                               marker=self.closure_data_marker,
                               color=self.closure_line_color)

        self.draw()
        self.update_background()

    def get_closet_coordinates_from_x(self, x: int, x_data: List, y_data: List) -> Tuple[int, int]:
        """
        Return a tuple representing the closet point in the given x_data and y_data
        based on the given x value.
        """
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

        If the user is dragging the plot, then we pan the plot.
        """
        self.restore_region(self.background)
        if not event.inaxes:
            self.covid_horizontal_cross_hair.set_visible(False)
            self.covid_vertical_cross_hair.set_visible(False)
            self.closure_horizontal_cross_hair.set_visible(False)
            self.closure_vertical_cross_hair.set_visible(False)
            self.curr_x = None
            self.curr_y = None
            self.blit(self.figure.bbox)
            self.flush_events()
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
        """
        Return the new limit(minimum and maximum) based on several zooming factors centered on x.
        """
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
        Zoom in or zoom out as the user scroll up or down.
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
        """
        If the left button is pressed, we start pan the plot as the mouse move.
        This function serve as the start of the pan operation.
        """
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
        """
        If the left button is released, we end the pan.
        """
        if event.button == matplotlib.backend_bases.MouseButton.LEFT:
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
    # Window sizes
    width: int = 1200
    height: int = int(1200 * 0.618)

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
    github_label: StandardLabel

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

    # Menu bar
    menu_bar: StandardMenuBar
    file_menu: QMenu
    edit_menu: QMenu
    settings_menu: QMenu
    view_menu: QMenu

    progress_bar: StandardProgressBar

    def __init__(self, *args, **kwargs) -> None:
        """
        Init the whole UI.
        """
        super(MainWindowUI, self).__init__(*args, **kwargs)
        self.init_window()

    def init_window(self) -> None:
        """Init the main window UI"""
        # Set the window width as the 0.6 of the available geometry.
        desktop = QDesktopWidget()
        desktop_geometry = desktop.availableGeometry(desktop.primaryScreen())
        new_width = int(desktop_geometry.width() * 0.6)
        if new_width > self.width:
            self.width = int(new_width)
            self.height = int(self.width * 0.618)

        self.resize(self.width, self.height)
        self.setFixedSize(self.size())

        # Center the window
        frame_geometry = self.frameGeometry()
        center_point = desktop_geometry.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

        # Set window title
        self.setWindowTitle('Educational Crisis - A Closer Examination on the Correlations Between '
                            'Covid-19 and School Closures Around the Globe')

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
        self.initialization_button.setToolTip('Initialize/Re-initialize the data')
        self.github_label = StandardLabel('<a href="https://github.com/UofT-CS-Group/'
                                          'CSC110-Final-Project"> Our GitHub Repository </a>',
                                          self.initialization_group)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setAlignment(Qt.AlignCenter)
        self.github_label.setToolTip('Click to open our GitHub repository page')

        # Location Group
        self.location_group = StandardGroupBox('Location', self)
        self.country_search_label = StandardLabel('Search', self.location_group)
        self.country_search_bar = StandardLineEdit(parent=self.location_group)
        self.country_search_bar.setToolTip('Type in the country you would like to search')
        self.country_selection_label = StandardLabel('Country', self.location_group)
        self.country_selection_combo_box = StandardComboBox(self.location_group)
        self.global_helper_label = StandardLabel('Global View')
        self.global_radio_button = StandardRadioButton('Global', self.location_group)
        self.global_radio_button.setToolTip('Use global data')
        self.country_shortcut_buttons = [StandardPushButton(c.name, self.location_group)
                                         for c in data.KEY_COUNTRIES]
        for button in self.country_shortcut_buttons:
            button.setToolTip(button.text())
        self.location_reset_button = StandardPushButton('Reset', self.location_group)
        self.location_reset_button.setToolTip('Reset the location selection')

        # Date Group
        self.date_group = StandardGroupBox('Date', self)
        self.start_date_label = StandardLabel('Start Date: ', self.date_group)
        self.start_date_edit = StandardDateEdit(self.date_group)
        self.start_date_slider = StandardSlider(parent=self.date_group)
        self.start_date_slider.setToolTip('Use the slider to set the start date')
        self.end_date_label = StandardLabel('End Date: ', self.date_group)
        self.end_date_edit = StandardDateEdit(self.date_group)
        self.end_date_slider = StandardSlider(parent=self.date_group)
        self.end_date_slider.setToolTip('Use the slider to set the end date')
        self.date_reset_button = StandardPushButton('Reset', self.date_group)
        self.date_reset_button.setToolTip('Reset the date')
        self.date_confirm_button = StandardPushButton('Confirm', self.date_group)
        self.date_confirm_button.setToolTip('Confirm the date selection and update the plot')

        # Plot
        self.plot_canvas = PlotCanvas()
        self.plot_tool_bar = PlotToolbar(self.plot_canvas, self)

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
        self.settings_menu = self.menu_bar.addMenu('Settings')
        self.view_menu = self.menu_bar.addMenu('View')

        self.setMenuBar(self.menu_bar)

    def init_layout(self) -> None:
        """
        Init the layout for all widgets.
        """
        widget = QWidget(self)
        # The main layout of the main window
        main_layout = QVBoxLayout(widget)

        controller_layout = QHBoxLayout()

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
        initialization_group_layout.addWidget(self.github_label, 1)

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
            shortcut_layout = QHBoxLayout()
            location_group_layout.addLayout(shortcut_layout, row, 0, 1, 2)
            for column in range(2):
                shortcut_layout.addWidget(self.country_shortcut_buttons[index], 2)
                index += 1

        location_group_layout.addWidget(self.location_reset_button, 4, 2)

        # Date Group
        controller_layout.addWidget(self.date_group)
        date_group_layout = EnhancedVBoxLayout(self.date_group)
        date_group_layout.add_widget(self.start_date_label, 0, alignment=Qt.AlignLeft)
        date_group_layout.add_widget(self.start_date_edit, 1, stretch=1000 - 618)
        date_group_layout.add_widget(self.start_date_slider, 1, stretch=618)
        date_group_layout.add_widget(self.end_date_label, 2, alignment=Qt.AlignLeft)
        date_group_layout.add_widget(self.end_date_edit, 3, stretch=1000 - 618)
        date_group_layout.add_widget(self.end_date_slider, 3, stretch=618)
        date_group_layout.insertSpacerItem(4, QSpacerItem(100, 30))
        date_group_layout.add_widget(self.date_confirm_button, 4, stretch=618)
        date_group_layout.add_widget(self.date_reset_button, 4, stretch=1000 - 618)

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
            # If the description contains "Failed to", meaning that some critical errors happened.
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
    is_slider_moving: bool = False

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
        # File menu
        save_plot = QAction('Save Current Plot', self)
        save_plot.setStatusTip('Save the current plot into a file')
        save_plot.setShortcut('Ctrl+S')
        save_plot.triggered.connect(self.save_plot)
        self.file_menu.addAction(save_plot)

        separator = QAction(self)
        separator.setSeparator(True)
        self.file_menu.addAction(separator)

        exit_action = QAction('Exit Application', self)
        exit_action.setStatusTip('Exit application')
        # Ctrl+W is the close shortcut for most programs. (Also Alt+F4)
        exit_action.setShortcut('Ctrl+W')
        exit_action.triggered.connect(self.exit)
        self.file_menu.addAction(exit_action)

        # Edit Menu
        rename_window = QAction('Rename Main Window', self)
        rename_window.setStatusTip('Rename the main window')
        rename_window.setShortcut('Ctrl+R')
        rename_window.triggered.connect(self.rename_main_window)
        self.edit_menu.addAction(rename_window)

        # Settings menu
        # Set settings menu to be disabled before initialization,
        # because it crashes if we try to edit the settings of an empty graph
        self.settings_menu.setDisabled(True)

        # Different color settings
        line_color_menu = self.settings_menu.addMenu('Line Color')

        # COVID Colors
        color_covid = QAction('COVID-19 Cases Line Color', self)
        color_covid.setStatusTip('Select the line color of the COVID-19 Cases plot')
        color_covid.triggered.connect(lambda: self.change_color(self.plot_canvas.covid_axes))
        # Closure Colors
        color_closure = QAction('School Closure Status Line Color', self)
        color_closure.setStatusTip('Select the line color of the School Closure Status plot')
        color_closure.triggered.connect(lambda: self.change_color(self.plot_canvas.closure_axes))

        line_color_menu.addActions([color_covid, color_closure])

        # Different Line style settings
        line_style_menu = self.settings_menu.addMenu('Line Style')
        covid_style_menu = line_style_menu.addMenu('COVID-19 Cases Line Style')
        closure_style_menu = line_style_menu.addMenu('School Closure Status Line Style')

        # COVID Styles
        for style, description in LINE_STYLES.items():
            covid_action = QAction(description, covid_style_menu)
            covid_action.setStatusTip(description)
            covid_action.triggered.connect(make_function(self.plot_canvas.update_lines,
                                                         self.plot_canvas.covid_axes,
                                                         style=style))
            covid_style_menu.addAction(covid_action)

            closure_action = QAction(description, closure_style_menu)
            closure_action.setStatusTip(description)
            closure_action.triggered.connect(make_function(self.plot_canvas.update_lines,
                                                           self.plot_canvas.closure_axes,
                                                           style=style))
            closure_style_menu.addAction(closure_action)

        # Show marker toggle menu
        marker_menu = self.settings_menu.addMenu('Markers')
        covid_marker_menu = marker_menu.addMenu('COVID-19 Cases Line Marker')
        closure_marker_menu = marker_menu.addMenu('School Closure Status Line Marker')

        for marker, info in LINE_MARKERS.items():
            description, icon_name = info
            covid_action = QAction(description, covid_marker_menu)
            covid_action.setIcon(QIcon(f'resources/assets/markers/{icon_name}'))
            covid_action.setStatusTip(description)
            covid_action.triggered.connect(make_function(self.plot_canvas.update_lines,
                                                         self.plot_canvas.covid_axes,
                                                         marker=marker))
            covid_marker_menu.addAction(covid_action)

            closure_action = QAction(description, closure_marker_menu)
            closure_action.setIcon(QIcon(f'resources/assets/markers/{icon_name}'))
            closure_action.setStatusTip(description)
            closure_action.triggered.connect(make_function(self.plot_canvas.update_lines,
                                                           self.plot_canvas.closure_axes,
                                                           marker=marker))
            closure_marker_menu.addAction(closure_action)

        # View Menu
        view_statusbar = QAction('Display Statusbar', self)
        view_statusbar.setCheckable(True)
        view_statusbar.setChecked(True)
        view_statusbar.setStatusTip('Turn on/off the statusbar')
        view_statusbar.triggered.connect(self.toggle_statusbar)
        self.view_menu.addAction(view_statusbar)

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
        self.start_date_slider.sliderReleased.connect(self.on_slider_released)
        self.start_date_slider.valueChanged.connect(self.on_start_date_slider_value_changed)
        self.end_date_slider.sliderMoved.connect(self.on_end_date_slider_moved)
        self.end_date_slider.sliderReleased.connect(self.on_slider_released)
        self.end_date_slider.valueChanged.connect(self.on_end_date_slider_value_changed)

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
            self.initialization_helper_label.setText(
                    'Please click the button below \nto reinitialize our data!')
            self.settings_menu.setDisabled(False)
            self.plot_canvas.plotted = True

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
        When the texts in the search bar are edited by the user, then we update the current country
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
        """
        When the user selects a new country, we update the plot correspondingly.
        """
        self.update_plot()

    @pyqtSlot()
    def on_country_shortcut_buttons_clicked(self) -> None:
        """
        When the user clicks a country shortcut button,
        we update the plot and other widgets correspondingly.
        """
        # This could actually get the sender button.
        button = self.sender()
        country_name = button.text()
        self.country_selection_combo_box.setCurrentText(country_name)
        self.global_radio_button.setChecked(False)

    @pyqtSlot()
    def on_location_reset_button_clicked(self) -> None:
        """
        When the user clicks the location reset button, then we set the locations to the default
        values and update the plot.
        """
        self.set_default_location()
        self.update_plot()

    @pyqtSlot()
    def on_date_confirm_button_clicked(self) -> None:
        """
        When the user clicks the date confirm button, then we update the plot according to the
        selected dates.
        """
        self.update_plot()

    @pyqtSlot()
    def on_date_reset_button_clicked(self) -> None:
        """
        When the user clicks the date reset button, then we set the date to the default
        values and update the plot.
        """
        self.set_default_date()
        self.update_plot()

    def on_date_edit_changed(self, new_date: QDate, date_slider: StandardSlider) -> None:
        """
        When the date is edited by the user,
        we update the tick of the slider to the correct position.
        """
        if not self.is_user_operation:
            return
        new_date = new_date.toPyDate()
        min_date = self.start_date_edit.minimumDate().toPyDate()
        max_date = self.end_date_edit.maximumDate().toPyDate()
        delta1 = new_date - min_date
        delta2 = max_date - min_date
        self.is_slider_moving = True
        date_slider.setValue(math.ceil((delta1 / delta2) * 100))
        self.is_slider_moving = False

    @pyqtSlot(QDate)
    def on_start_date_edit_changed(self, new_date: QDate) -> None:
        """
        When the user changes the start date edit, then we first validate the date and then update
        other widgets.
        If the date is not valid (start > end), then we will intimidate the user by popping a
        warning messagebox.
        """
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
        """
        When the user changes the end date edit, then we first validate the date and then update
        other widgets.
        If the date is not valid (start > end), then we will intimidate the user by popping a
        warning messagebox.
        """
        min_qdate = self.start_date_edit.date()
        min_date = min_qdate.toPyDate()
        if new_date.toPyDate() < min_date:
            QMessageBox.warning(self, 'Warning', 'End date should not be smaller than start date!',
                                QMessageBox.Ok, QMessageBox.Ok)
            self.end_date_edit.setDate(min_qdate)
            self.on_date_edit_changed(min_qdate, self.end_date_slider)
        else:
            self.on_date_edit_changed(new_date, self.end_date_slider)

    def on_slider_value_changed(self, percentage: float, date_edit: StandardDateEdit) -> None:
        min_date = self.start_date_edit.minimumDate().toPyDate()
        max_date = self.end_date_edit.maximumDate().toPyDate()
        delta = max_date - min_date
        delta *= percentage
        self.is_user_operation = False
        date_edit.setDate(min_date + delta)
        self.is_user_operation = True

    def on_slider_moved(self, percentage: float, date_edit: StandardDateEdit) -> None:
        """
        When the user moves the slider, we update the date_edit to display the correct date.
        """
        self.is_slider_moving = True
        self.on_slider_value_changed(percentage, date_edit)

    @pyqtSlot(int)
    def on_start_date_slider_moved(self, new_value: int) -> None:
        """
        When the user moves the start date slider, then we firstly prevent invalid changes and
        update other widgets.
        """
        if new_value > self.end_date_slider.value():
            self.start_date_slider.setValue(self.end_date_slider.value())
            return
        percentage = new_value / self.start_date_slider.maximum()
        self.on_slider_moved(percentage, self.start_date_edit)

    @pyqtSlot(int)
    def on_end_date_slider_moved(self, new_value: int) -> None:
        """
        When the user moves the end date slider, then we firstly prevent invalid changes and
        update other widgets.
        """
        if new_value < self.start_date_slider.value():
            self.end_date_slider.setValue(self.start_date_slider.value())
            return
        percentage = new_value / self.end_date_slider.maximum()
        self.on_slider_moved(percentage, self.end_date_edit)

    @pyqtSlot()
    def on_slider_released(self):
        self.is_slider_moving = False

    @pyqtSlot(int)
    def on_start_date_slider_value_changed(self, new_value: int):
        if self.is_slider_moving:
            return
        if new_value > self.end_date_slider.value():
            self.start_date_slider.setValue(self.end_date_slider.value())
            return
        percentage = new_value / self.start_date_slider.maximum()
        self.on_slider_value_changed(percentage, self.start_date_edit)

    @pyqtSlot(int)
    def on_end_date_slider_value_changed(self, new_value: int):
        if self.is_slider_moving:
            return
        if new_value < self.start_date_slider.value():
            self.end_date_slider.setValue(self.start_date_slider.value())
            return
        percentage = new_value / self.end_date_slider.maximum()
        self.on_slider_value_changed(percentage, self.end_date_edit)

    @pyqtSlot()
    def save_plot(self) -> None:
        """Saves the current plots at the specified location"""
        file_dialog = StandardFileDialog()

        # The second return value is "Selected filter", which is useless
        path, _ = file_dialog.getSaveFileName(self, "Save Plot Image", "", "PNG(*.png)")

        if path == '':
            # This is because the user may press cancel
            return

        # Saving canvas at desired path
        self.plot_canvas.print_png(path)

    def change_color(self, axes: matplotlib.axes.Axes) -> None:
        """Changes the line color in the plot to a specific color as given."""
        color_dialog = StandardColorDialog()
        ok = color_dialog.exec()
        if ok:
            color = color_dialog.currentColor().name()
            self.plot_canvas.update_lines(axes, color)

    @pyqtSlot()
    def exit(self) -> None:
        """Closes the application the moment when triggered"""
        QApplication.quit()

    @pyqtSlot()
    def rename_main_window(self) -> None:
        """Rename the main window depends on what users typed in."""
        rename_dialog = StandardInputDialog(self)
        rename_dialog.setWindowTitle('Rename the Main Window')
        rename_dialog.setLabelText('Please enter the new window title: ')
        rename_dialog.resize(400, 100)
        rename_dialog.show()
        ok = rename_dialog.exec()
        new_name = rename_dialog.textValue()

        if ok and new_name != '':
            self.setWindowTitle(new_name)

    @pyqtSlot(bool)
    def toggle_statusbar(self, state: bool) -> None:
        """Toggles the statusbar (visible or invisible)."""
        if state:
            self.statusBar().setVisible(True)
        else:
            self.statusBar().setVisible(False)
