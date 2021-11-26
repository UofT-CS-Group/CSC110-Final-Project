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
import resource_manager
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

    logging.info('Registering resources...')
    resource_manager.register_resources()
    logging.info('Resources registered!')

    # Create the QApplication instance.
    app = QApplication(sys.argv)

    # If failed to download the icon, then let user know and continue running the program
    logging.info('Initializing icons...')
    if not resource_manager.init_resource(
            resource_manager.RESOURCES_DICT[resource_manager.ICON_RESOURCE_NAME]):
        logging.critical('Failed to download icons!')
        # Pls ignore the warning of the None, this is good.
        QMessageBox.critical(None, 'Critical', 'Failed to download icons! \n'
                                               'You will not see our icons of our program. :<',
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
