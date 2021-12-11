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
from typing import Callable, List

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
