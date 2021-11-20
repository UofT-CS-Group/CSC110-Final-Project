"""
The main entry of our program.
"""
import logging
import sys

from PyQt5.QtWidgets import *

import gui
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
if __name__ == '__main__':
    logging.info('Starting application...')

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
