"""
The main entry of our program.
"""
import sys
import time

import gui
import data
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


if __name__ == '__main__':
    data.logging.info('Starting application...')

    # Initialize all data on another thread because we don't want it to block our main thread
    # for 15 seconds.
    data_thread = threading.Thread(target=data.init_data, name='data_thread')
    data_thread.start()

    data.logging.info(f'Current Running Threads: {threading.enumerate()}')

    # Create the QApplication instance.
    app = QApplication(sys.argv)

    init_window = gui.InitWindow()
    init_window.show()
    
    # We need to retain a reference here to avoid garbage collection.
    # main_window will be initialized after the data are fully loaded
    # in gui.InitWindow#update_progress_bar method.
    main_window: gui.MainWindow
    
    # Start the event loop with app.exec
    # After the program stopped, app.exec will return a exit code which could indicate
    # whether there is an error, and sys.exit will get it.
    # If we don't call it with sys.exit, the exit code will always be 0 no matter if an
    # error happened.
    sys.exit(app.exec_())
