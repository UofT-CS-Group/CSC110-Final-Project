"""
Main GUI + backend here
I know it's in efficient and shitty
Just for temp use
"""
import threading
import time
import typing

import QtDesigner
import numpy as np
import algorithms
import datetime
import settings
import data

from typing import Iterable, List

import matplotlib.lines
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot
import matplotlib.style

import matplotlib.backend_bases
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

matplotlib.style.use('fast')


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


class StandardDateEdit(QDateEdit):
    """
    A standard date edit for our project.
    
    When needed, we could add more attributes and functions.
    """
    
    def __init__(self, *__args):
        super().__init__(*__args)
        set_font(self)


class StandardCheckbox(QCheckBox):
    """
    A standard checkbox for our project.

    When needed, we could add more attributes and functions.
    """
    
    def __init__(self, text: str, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(text, parent)
        set_font(self)


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
        self.axes_covid, self.axes_closure = self.figure.subplots(2, 1)
        super(PlotCanvas, self).__init__(self.figure)
        self.mpl_connect("motion_notify_event", self.on_mouse_move)
    
    def plot_covid_cases(self, covid_cases: List[data.CovidCaseData]) -> None:
        x_axis = [c.date for c in covid_cases]
        y_axis = [c.cases for c in covid_cases]
        self.covid_x_data = x_axis
        self.covid_y_data = y_axis
        self.axes_covid.clear()
        self.axes_covid.plot(x_axis, y_axis, marker='.', color='orange')
        for text in self.axes_covid.get_xticklabels():
            text.set_rotation(40.0)
        self.draw()
        self.is_covid_cross_hair_init = False
    
    def plot_school_closures(self, school_closures: List[data.SchoolClosureData]) -> None:
        x_axis = [c.date for c in school_closures]
        y_axis = [c.status.value for c in school_closures]
        self.closure_x_data = x_axis
        self.closure_y_data = y_axis
        self.axes_closure.clear()
        self.axes_closure.plot(x_axis, y_axis, marker='.', color='green')
        self.axes_closure.set_yticks(ticks=[0, 1, 2, 3], minor=False)
        self.axes_closure.set_yticklabels(labels=['Academic Break', 'Fully Open', 'Partially Open', 'Closed'],
                                          minor=False)
        for text in self.axes_closure.get_xticklabels():
            text.set_rotation(40.0)
        self.draw()
        self.is_closure_cross_hair_init = False
    
    def on_mouse_move(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        # The reason why the cross-hair is laggy is because self.draw() takes a very long time to draw.
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
                    self.covid_horizontal_cross_hair = self.axes_covid.axhline(y=y, color='black', linewidth=0.8,
                                                                               linestyle='--')
                    self.covid_vertical_cross_hair = self.axes_covid.axvline(x=real_x, color='black', linewidth=0.8,
                                                                             linestyle='--')
                    self.is_covid_cross_hair_init = True
                
                self.covid_horizontal_cross_hair.set_visible(True)
                self.covid_vertical_cross_hair.set_visible(True)
                
                self.covid_horizontal_cross_hair.set_ydata(y)
                self.covid_vertical_cross_hair.set_xdata(real_x)
                self.draw()
            elif event.inaxes == self.axes_closure:
                index = algorithms.binary_search(self.closure_x_data, x_date)
                x = self.closure_x_data[index]
                y = self.closure_y_data[min(index + 1, len(self.closure_y_data) - 1)]
                real_x = (x - datetime.date.fromtimestamp(0)).days
                
                if not self.is_closure_cross_hair_init:
                    self.closure_horizontal_cross_hair = self.axes_closure.axhline(y=y, color='black', linewidth=0.8,
                                                                                   linestyle='--')
                    self.closure_vertical_cross_hair = self.axes_closure.axvline(x=real_x, color='black', linewidth=0.8,
                                                                                 linestyle='--')
                    self.is_closure_cross_hair_init = True
                
                self.closure_horizontal_cross_hair.set_visible(True)
                self.closure_vertical_cross_hair.set_visible(True)
                
                self.closure_horizontal_cross_hair.set_ydata(y)
                self.closure_vertical_cross_hair.set_xdata(real_x)
                self.draw()
        else:
            if self.is_covid_cross_hair_init:
                if self.covid_horizontal_cross_hair.get_visible() and self.covid_vertical_cross_hair.get_visible():
                    self.covid_horizontal_cross_hair.set_visible(False)
                    self.covid_vertical_cross_hair.set_visible(False)
                    self.draw()
            if self.is_closure_cross_hair_init:
                if self.closure_horizontal_cross_hair.get_visible() and self.closure_vertical_cross_hair.get_visible():
                    self.closure_horizontal_cross_hair.set_visible(False)
                    self.closure_vertical_cross_hair.set_visible(False)
                    self.draw()


class MainWindow(QMainWindow):
    """
    The main window of our program.
    """
    
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
        self.resize(1400, 865)
        
        # Center the window
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
        # Set window title
        self.setWindowTitle('Main Window')
        
        # Initialize status bar
        self.statusBar().showMessage('Ready.')
        
        # Initialize Widgets
        self.init_widgets()
        
        # Initialize Layout
        self.init_layout()
        
        # Initialize signals (events)
        self.init_signals()
    
    def init_widgets(self) -> None:
        """
        Init all widgets attributes.
        """
        # Country selections
        self.country_selection_label = StandardLabel('Country: ')
        self.country_selection_combo_box = StandardComboBox(self)
        
        self.global_checkbox = StandardCheckbox('Global', self)
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
        self.start_date_edit.setMinimumDate(data.ALL_COVID_CASES[0].date)
        self.start_date_edit.setMaximumDate(data.ALL_COVID_CASES[-2].date)
        self.end_date_edit.setMinimumDate(data.ALL_COVID_CASES[1].date)
        self.end_date_edit.setMaximumDate(data.ALL_COVID_CASES[-1].date)
        self.end_date_edit.setDate(data.ALL_COVID_CASES[-1].date)
        
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
        main_layout = QHBoxLayout()
        
        # The layout for our options controller
        controller_layout = QVBoxLayout()
        # Golden Ratio 0.618 : 1
        main_layout.addLayout(controller_layout, 382)
        controller_layout.addStretch(1)
        
        # For temp use
        # TODO: Better Layout
        checkbox_layout = QHBoxLayout(self)
        controller_layout.addLayout(checkbox_layout)
        checkbox_layout.addWidget(self.global_checkbox)
        checkbox_layout.addWidget(self.country_checkbox)
        
        # The layout for country, province, and city selection
        location_selection_layout = QFormLayout()
        controller_layout.addLayout(location_selection_layout)
        location_selection_layout.addRow(self.country_selection_label, self.country_selection_combo_box)
        location_selection_layout.addRow(self.province_selection_label, self.province_selection_combo_box)
        location_selection_layout.addRow(self.city_selection_label, self.city_selection_combo_box)
        
        # The layout for date range
        date_range_layout = QFormLayout()
        controller_layout.addLayout(date_range_layout)
        date_range_layout.addRow(self.start_date_label, self.start_date_edit)
        date_range_layout.addRow(self.end_date_label, self.end_date_edit)
        
        controller_layout.addWidget(self.confirm_button)
        
        # The layout for our plot
        plot_layout = QVBoxLayout()
        main_layout.addLayout(plot_layout, 618)
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
        self.country_checkbox.stateChanged.connect(self.on_country_checkbox_changed)
        
        self.confirm_button.clicked.connect(self.confirm_button_handler)
        self.confirm_button_handler()
        
        self.country_selection_combo_box.currentIndexChanged.connect(self.on_country_selection_changed)
        self.province_selection_combo_box.currentIndexChanged.connect(self.on_province_selection_changed)
    
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
            filtered_covid_cases = algorithms.linear_predicate(data.GLOBAL_COVID_CASES,
                                                               lambda item: start_date <= item.date <= end_date)
            filtered_school_closures = algorithms.linear_predicate(data.GLOBAL_SCHOOL_CLOSURES,
                                                                   lambda item: start_date <= item.date <= end_date)
        else:
            country = data.Country(self.country_selection_combo_box.currentText())
            # This is because some of the country names in school closures
            # are not the same as the covid datasets
            # TODO Fix it
            if country not in data.COUNTRIES_TO_ALL_COVID_CASES or country not in data.COUNTRIES_TO_ALL_SCHOOL_CLOSURES:
                message_box = QMessageBox(QMessageBox.Critical, 'Error', 'This country does not have any data!',
                                          QMessageBox.Ok)
                message_box.exec_()
                return
            
            if self.country_checkbox.isChecked():
                filtered_covid_cases = algorithms.linear_predicate(data.COUNTRIES_TO_COVID_CASES[country],
                                                                   lambda item: start_date <= item.date <= end_date)
            else:
                province = data.Province(self.province_selection_combo_box.currentText(), country)
                city = data.City(self.city_selection_combo_box.currentText(), province)
                filtered_covid_cases = algorithms.linear_predicate(data.COUNTRIES_TO_ALL_COVID_CASES[country],
                                                                   lambda item: (province.name == '' or
                                                                                 item.province == province) and
                                                                                (city.name == '' or
                                                                                 item.city == city) and
                                                                                start_date <= item.date <= end_date)

            filtered_school_closures = algorithms.linear_predicate(data.COUNTRIES_TO_ALL_SCHOOL_CLOSURES[country],
                                                                   lambda item: start_date <= item.date <= end_date)

        self.plot_canvas.plot_school_closures(filtered_school_closures)
        self.plot_canvas.plot_covid_cases(filtered_covid_cases)
    
    def on_country_selection_changed(self, index: int) -> None:
        """
        Things to do when user select a country.
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
    
    def on_province_selection_changed(self, index: int) -> None:
        """
        Things to do when user select a province.
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
    
    def on_global_checkbox_changed(self, state: int) -> None:
        if state == Qt.Checked:
            self.country_selection_combo_box.clear()
            self.province_selection_combo_box.clear()
            self.city_selection_combo_box.clear()
            self.country_checkbox.setChecked(False)
        else:
            self.set_default_location_selection()
    
    def on_country_checkbox_changed(self, state: int) -> None:
        if state == Qt.Checked:
            self.global_checkbox.setChecked(False)
            self.province_selection_combo_box.clear()
            self.city_selection_combo_box.clear()
        else:
            country = data.SORTED_COUNTRIES[self.country_selection_combo_box.currentIndex()]
            if country in data.COUNTRIES_TO_PROVINCES:
                self.province_selection_combo_box.addItems([p.name for p in data.COUNTRIES_TO_PROVINCES[country]])
    
    def set_default_location_selection(self):
        self.country_selection_combo_box.clear()
        self.country_selection_combo_box.addItems(c.name for c in data.SORTED_COUNTRIES)
        default_country = data.Country('Canada')
        self.country_selection_combo_box.setCurrentIndex(data.SORTED_COUNTRIES.index(default_country))
        default_provinces = data.COUNTRIES_TO_PROVINCES[default_country]
        self.province_selection_combo_box.clear()
        self.province_selection_combo_box.addItems(p.name for p in default_provinces)
        self.city_selection_combo_box.clear()
