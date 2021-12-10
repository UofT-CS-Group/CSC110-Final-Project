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

from config_manager import ConfigManager

conf_manager = ConfigManager("resources/config.json")
conf = conf_manager.data


# Project sorting algorithm
def sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    return algorithms.merge_sort(lst, compare, reverse)


# =================================================================================================
# Font
# =================================================================================================
FONT_FAMILY = conf["setting"]["font"]["family"]
FONT_SIZE = int(conf["setting"]["font"]["size"])

# =================================================================================================
# Logger
# =================================================================================================
conf_level = conf["setting"]["log"]["level"]
if conf_level in ["critical", "error", "warning", "info", "debug", "notset"]:
    if conf_level == "critical":
        LOG_LEVEL = logging.CRITICAL
    if conf_level == "error":
        LOG_LEVEL = logging.ERROR
    if conf_level == "warning":
        LOG_LEVEL = logging.WARNING
    if conf_level == "info":
        LOG_LEVEL = logging.INFO
    if conf_level == "debug":
        LOG_LEVEL = logging.DEBUG
    if conf_level == "notset":
        LOG_LEVEL = logging.NOTSET
LOG_FORMAT = conf["setting"]["log"]["format"]
