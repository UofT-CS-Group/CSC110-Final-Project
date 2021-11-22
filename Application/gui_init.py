"""
The initialization window of our project.

We may delete it in the future.
"""
# Python built-ins
import math
import time

# Our modules
import algorithms
import data
import gui_main
import main
from gui_utils import *


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
            main.main_window = gui_main.MainWindow()
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

    def closeEvent(self, a0: QCloseEvent) -> None:
        """
        Handle the things to do after the user press the red close button on the right corner.
        """
        if not self.is_complete:
            import _thread
            _thread.interrupt_main()
        else:
            super(InitWindow, self).closeEvent(a0)
