"""
This file contains all settings for our project.

Settings include:
    - Fonts
    - Project sorting algorithms
    - Logger
    - And more...
"""
# Python built-ins
import logging
from typing import Callable, Dict, List

# Our modules
import algorithms
from algorithms import T


# Project sorting algorithm
def sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    """Sorts the lst using the function compare"""
    return algorithms.merge_sort(lst, compare, reverse)


# =================================================================================================
# Font
# =================================================================================================
FONT_FAMILY = 'Calibri'
ALT_FONT_FAMILY = 'Helvetica'
FONT_SIZE = 14

# =================================================================================================
# Logger
# =================================================================================================

LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s] - %(levelname)s - %(message)s'


def init_setting(setting_config: Dict) -> None:
    """
    Init all settings from setting_config.
    """
    global FONT_FAMILY
    FONT_FAMILY = setting_config['font_family']
    global ALT_FONT_FAMILY
    ALT_FONT_FAMILY = setting_config['alternative_font_family']
    global FONT_SIZE
    FONT_SIZE = setting_config['font_size']


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    import python_ta.contracts

    python_ta.contracts.check_all_contracts()

    import python_ta

    python_ta.check_all(config={
        'extra-imports'  : ['logging', 'typing', 'algorithms'],
        'allowed-io'     : [],
        'max-line-length': 100,
        'disable'        : ['R1705', 'C0200', 'E9989', 'E9997']
    })
