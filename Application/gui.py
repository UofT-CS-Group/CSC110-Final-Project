"""
Main GUI + backend here
I know it's in efficient and shitty
Just for temp use
"""

import datetime

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import numpy as np
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot

from typing import Iterable

import algorithms
import settings
import data


def set_font(widget: QWidget,
             font_family: str = settings.FONT_FAMILY,
             font_size: int = settings.FONT_SIZE) -> None:
    """
    Set the font of given widget to given font and size.
    """
    font: QFont = widget.font()
    font.setFamily(font_family)
    font.setPointSize(font_size)
    widget.setFont(font)


class StandardLabel(QLabel):
    
    def __init__(self, text: str = ''):
        super(StandardLabel, self).__init__()
        set_font(self)
        
        # Set Default Text
        self.setText(text)


class StandardPushButton(QPushButton):
    
    def __init__(self, text: str = '', *__args):
        super().__init__(*__args)
        set_font(self)
        self.setText(text)


class StandardComboBox(QComboBox):
    
    def __init__(self, parent=None, items: Iterable = None):
        super().__init__(parent)
        set_font(self)
        self.addItems(items)


class StandardDateEdit(QDateEdit):
    
    def __init__(self, *__args):
        super().__init__(*__args)
        set_font(self)


class PlotCanvas(FigureCanvas):
    figure: pyplot.Figure
    axes: pyplot.Axes
    
    def __init__(self) -> None:
        self.figure, self.axes = pyplot.subplots()
        super(PlotCanvas, self).__init__(self.figure)


class MainWindow(QMainWindow):
    init_button: StandardPushButton
    
    plot_navigation_tool_bar: NavigationToolbar
    plot_canvas: PlotCanvas
    
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
        # Country selections
        self.country_selection_label = StandardLabel('Country: ')
        self.country_selection_combo_box = StandardComboBox(self, [c.name for c in data.SORTED_COUNTRIES])
        default_country = data.Country('Canada')
        self.country_selection_combo_box.setCurrentIndex(data.SORTED_COUNTRIES.index(default_country))
        
        # Province selection
        default_provinces = algorithms.linear_predicate(data.SORTED_PROVINCES, lambda p: p.country == default_country)
        self.province_selection_label = StandardLabel('Province: ')
        self.province_selection_combo_box = StandardComboBox(self, [p.name for p in default_provinces])
        
        # City selection
        default_cities = algorithms.linear_predicate(data.SORTED_CITIES, lambda c: c.province == default_provinces[0])
        self.city_selection_label = StandardLabel('City: ')
        self.city_selection_combo_box = StandardComboBox(self, [c.name for c in default_cities])
        
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
        # The main layout of the main window
        main_layout = QHBoxLayout()
        
        # The layout for our options controller
        controller_layout = QVBoxLayout()
        # Golden Ratio 0.618 : 1
        main_layout.addLayout(controller_layout, 382)
        controller_layout.addStretch(1)
        
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
        self.confirm_button.clicked.connect(self.confirm_button_handler)
        
        self.country_selection_combo_box.currentIndexChanged.connect(self.on_country_selection_changed)
        self.province_selection_combo_box.currentIndexChanged.connect(self.on_province_selection_changed)
    
    def confirm_button_handler(self) -> None:
        country = data.Country(self.country_selection_combo_box.currentText())
        province = data.Province(self.province_selection_combo_box.currentText(), country)
        city = data.City(self.city_selection_combo_box.currentText(), province)
        
        q_start_date: QDate = self.start_date_edit.date()
        q_end_date: QDate = self.end_date_edit.date()
        start_date = datetime.date(q_start_date.year(), q_start_date.month(), q_start_date.day())
        end_date = datetime.date(q_end_date.year(), q_end_date.month(), q_end_date.day())
        
        lst = algorithms.linear_predicate(data.ALL_COVID_CASES,
                                          lambda item: (item.country == country) and
                                                       (province.name == '' or item.province == province) and
                                                       (city.name == '' or item.city == city) and
                                                       start_date <= item.date <= end_date)
        y_axis = [case.cases for case in lst]
        x_axis = [case.date for case in lst]
        
        self.plot_canvas.axes.clear()
        self.plot_canvas.axes.plot(x_axis, y_axis, linestyle='', marker='.', color='green')
        self.plot_canvas.draw()
    
    def on_country_selection_changed(self, index: int) -> None:
        country = data.SORTED_COUNTRIES[index]
        provinces = algorithms.linear_predicate(data.SORTED_PROVINCES, lambda p: p.country == country)
        cities = []
        if provinces:
            cities = algorithms.linear_predicate(data.SORTED_CITIES, lambda c: c.province == provinces[0])
        
        self.province_selection_combo_box.clear()
        if provinces:
            self.province_selection_combo_box.addItems([p.name for p in provinces])
        
        self.city_selection_combo_box.clear()
        if cities:
            self.city_selection_combo_box.addItems([c.name for c in cities])
    
    def on_province_selection_changed(self, index: int):
        country = data.SORTED_COUNTRIES[self.country_selection_combo_box.currentIndex()]
        province = algorithms.linear_predicate(data.SORTED_PROVINCES, lambda p: p.country == country)[index]
        cities = algorithms.linear_predicate(data.SORTED_CITIES, lambda c: c.province == province)
        
        self.city_selection_combo_box.clear()
        if cities:
            self.city_selection_combo_box.addItems([c.name for c in cities])
