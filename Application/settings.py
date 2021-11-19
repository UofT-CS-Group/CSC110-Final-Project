import algorithms

from algorithms import T
from typing import Callable, List

FONT_FAMILY = 'Calibri'
FONT_SIZE = 14


# Project sorting algorithm
def sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    return algorithms.merge_sort(lst, compare, reverse)
