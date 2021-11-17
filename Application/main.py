"""
The main entry of our program.
"""
import math
import os
import sys
import time

import psutil

import gui
import data
import threading

from typing import Callable, Any

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class InitWindowThread(threading.Thread):
    """
    The thread of the initialization window.
    """
    
    def __init__(self):
        super(InitWindowThread, self).__init__()
        self.setDaemon(True)
    
    def run(self) -> None:
        init_app = QApplication(sys.argv)
        
        init_window = gui.InitWindow()
        init_window.show()
        
        init_app.exec_()


if __name__ == '__main__':
    print('Initializing...')
    
    init_window_thread = InitWindowThread()
    init_window_thread.start()
    
    data.init_data()
    
    time.sleep(3.2)
    
    app = QApplication(sys.argv)
    
    main_window = gui.MainWindow()
    main_window.show()
    
    sys.exit(app.exec_())
