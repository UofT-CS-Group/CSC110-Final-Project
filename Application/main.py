"""
The main entry of our program.
"""
# Python built-ins
import logging
import sys

# PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

# Our modules
import gui_main
import settings
from resource_manager import *

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

    logging.info('Registering resources...')
    register_resources()
    logging.info('Resources registered!')

    # Create the QApplication instance.
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon('resources/assets/icon.png'))

    # If failed to download the icons, then let user know and continue running the program
    logging.info('Initializing icons...')
    if not init_resource(RESOURCES_DICT[ICON_RESOURCE_NAME]) or \
            any(not init_resource(RESOURCES_DICT[name]) for name in MARKERS_ICON_RESOURCE_NAMES):
        logging.critical('Failed to download icons!')
        # Pls ignore the warning of the None, this is good.
        QMessageBox.critical(None, 'Critical', 'Failed to download icons! \n'
                                               'You will not see some of the icons of our program.',
                             QMessageBox.Ok, QMessageBox.Ok)
    else:
        logging.info('Icon initialized!')

    main_window = gui_main.MainWindow()
    main_window.show()

    # Start the event loop with app.exec
    # After the program stopped, app.exec will return a exit code which could indicate
    # whether there is an error, and sys.exit will get it.
    # If we don't call it with sys.exit, the exit code will always be 0 no matter if an
    # error happened.
    exit_code = app.exec_()
    logging.info(f'Application stopped with exit code {exit_code}!')
    sys.exit(exit_code)
