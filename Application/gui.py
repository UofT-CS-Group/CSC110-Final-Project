"""
GUI File for main.py
"""

import sys
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic

import datetime

import data

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvas):
    """
    Class for the Matplotlib Canvas
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100) -> None:
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class PlotApplication(QtWidgets.QMainWindow):
    """
    Class for the actual application itself
    """
    def __init__(self) -> None:
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('plot_scatter.ui', self)
        self.resize(888, 600)
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap('something.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.setWindowIcon(icon)

        data.init_data()

        self.country_list = sorted(list({country.name for country in data.COUNTRIES}))

        self.comboBox.addItems(self.country_list)
        self.comboBox.currentIndexChanged.connect(self.update_country)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.ui.gridLayout_3.addWidget(self.canvas, 1, 1, 1, 1)
        self.ui.gridLayout_3.addWidget(self.toolbar, 0, 1, 1, 1)

        self.dateEdit.dateChanged.connect(self.update_start_date)
        self.dateEdit_2.dateChanged.connect(self.update_end_date)

        self.pushButton.clicked.connect(self.update_plot)

        # Defaults
        self.covid_cases = []
        self.dates = []
        self.country = 'China'
        self.comboBox.setCurrentIndex(self.country_list.index('China'))
        self.start_date = datetime.date(2020, 1, 22)
        self.end_date = datetime.date(2021, 1, 1)

    def update_country(self, value):
        self.country = self.country_list[value]

    def update_start_date(self, date):
        self.start_date = datetime.date(day=date.day(), month=date.month(), year=date.year())

    def update_end_date(self, date):
        self.end_date = datetime.date(day=date.day(), month=date.month(), year=date.year())

    def update_plot(self, value):
        self.covid_cases = []
        self.dates = []

        self.canvas.axes.clear()

        for case in data.ALL_COVID_CASES:
            if self.start_date <= case.date <= self.end_date and \
                    case.country == data.Country(self.country):
                self.covid_cases.append(case.cases)
                self.dates.append(case.date)

        # formatter = mdates.DateFormatter("%Y-%m-%d")
        # self.canvas.axes.xaxis.set_major_formatter(formatter)
        # self.canvas.axes.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        self.canvas.axes.plot([i for i in range(len(self.covid_cases))], self.covid_cases)
        # self.canvas.axes.autofmt_xdate()

        self.canvas.draw()


app = QtWidgets.QApplication(sys.argv)
mainWindow = PlotApplication()
mainWindow.show()
sys.exit(app.exec_())
