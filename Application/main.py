"""
The main entry of our program.
"""
# Python built-ins
import sys

# PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

# Our modules
import gui_main
from settings import *
from resource_manager import *

# =================================================================================================
# Initialize logger
# =================================================================================================
logging.basicConfig(stream=sys.stdout,
                    level=LOG_LEVEL,
                    format=LOG_FORMAT)


# =================================================================================================
# Main Chunk
# =================================================================================================


def init_icons() -> None:
    """Initializes icon for the application"""
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


# We need to retain a reference here to avoid garbage collection.
# main_window will be initialized after the data are fully loaded
# in gui.InitWindow#update_progress_bar method.
main_window: gui_main.MainWindow

if __name__ == '__main__':
    logging.info('Starting application...')

    logging.info('Loading config...')
    config = Config('config.json')
    logging.info('Config loaded!')

    logging.info('Initializing settings...')
    init_setting(config['setting'])
    logging.info('Settings initialized!')

    logging.info('Registering resources...')
    register_resources(config['resource'])
    logging.info('Resources registered!')

    # Create the QApplication instance.
    app = QApplication(sys.argv)

    init_icons()
    app.setWindowIcon(QIcon(RESOURCES_DICT[ICON_RESOURCE_NAME].local_path))

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
