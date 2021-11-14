"""
The main entry of our program.
"""
import sys
import gui
import data
import threading

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    print('Initializing...')
    # TODO Progress bar
    data.init_data()

    app = QApplication(sys.argv)
    
    main_window = gui.MainWindow()
    main_window.show()
    
    sys.exit(app.exec_())
