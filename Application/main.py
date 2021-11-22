"""
The main entry of our program.
"""
# Python built-ins
import logging
import sys

# PyQt5
from PyQt5.QtWidgets import *

# Our modules
import gui_main
import gui_init
import settings

# =================================================================================================
# Initialize logger
# =================================================================================================
logging.basicConfig(stream=sys.stdout,
                    level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)

# =================================================================================================
# Main Chunk
# =================================================================================================
# We need to retain a reference here to avoid garbage collection.
# main_window will be initialized after the data are fully loaded
# in gui.InitWindow#update_progress_bar method.
main_window: gui_main.MainWindow

if __name__ == '__main__':
    logging.info('Starting application...')

    # Create the QApplication instance.
    app = QApplication(sys.argv)

    init_window = gui_init.InitWindow()
    init_window.show()

    # Start the event loop with app.exec
    # After the program stopped, app.exec will return a exit code which could indicate
    # whether there is an error, and sys.exit will get it.
    # If we don't call it with sys.exit, the exit code will always be 0 no matter if an
    # error happened.
    sys.exit(app.exec_())
