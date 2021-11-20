"""
This file contains all settings used by the CSC110 Final Project

Settings include:
    - Fonts
    - Dataset links
    - And more...
"""
import logging
from typing import Callable, List

import algorithms
from algorithms import T


# Project sorting algorithm
def sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    return algorithms.merge_sort(lst, compare, reverse)


# =================================================================================================
# Font
# =================================================================================================
FONT_FAMILY = 'Calibri'
FONT_SIZE = 14

# =================================================================================================
# Files
# =================================================================================================
COVID19_US_URL = 'https://gist.githubusercontent.com/Lei-Tin/6581b1c27212fabdd35754dcc3d5de62/' \
                 'raw/c3597829095ea1c3ebe0cc6955b3a0d2febb9489/' \
                 'time_series_covid19_confirmed_US.csv'

COVID19_GLOBAL_URL = 'https://gist.githubusercontent.com/Lei-Tin/' \
                     '6581b1c27212fabdd35754dcc3d5de62/raw/' \
                     'c3597829095ea1c3ebe0cc6955b3a0d2febb9489/' \
                     'time_series_covid19_confirmed_global.csv'

CLOSURE_URL = 'https://gist.githubusercontent.com/Lei-Tin/' \
              '6581b1c27212fabdd35754dcc3d5de62/raw/c3597829095ea1c3ebe0cc6955b3a0d2febb9489/' \
              'full_dataset_31_oct.csv'

# MD5 Checksum Settings
BUFFER_SIZE = 65536
COVID19_US_MD5 = '7f0fe92c4337e03e122e98d28ee07c30'
COVID19_GLOBAL_MD5 = '93d4999c12dcf503d8e66cba5a93c3f7'
CLOSURE_MD5 = '9426167fdc1b664da627e74d84328c35'

# =================================================================================================
# Logger
# =================================================================================================
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s] - %(levelname)s - %(message)s'
