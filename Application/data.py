"""
This module contains all classes, functions, and constants for our data.
"""
# Python built-ins
import csv
import datetime
import logging
import math
from enum import Enum
from typing import Dict, List, Set

# Our modules
import algorithms
import resource_manager
import settings


# =================================================================================================
# Classes
# =================================================================================================


class ClosureStatus(Enum):
    """ A enum class that represents the closure status of schools.
    
    Note:
        - This class cannot be instantiated.
    """

    CLOSED = 3
    PARTIALLY_OPEN = 2
    FULLY_OPEN = 1
    ACADEMIC_BREAK = 0


class Location(object):
    """
    A class that represents a physical location in the world.

    Instance Attributes:
        - name: A string that represents the name of this location.
    """

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return self.name.__hash__()


class Country(Location):
    """
    A class that represents a country in the world.
    
    Instance Attributes:
        - name: A string that represents the name of this country.

    Representation Invariants:
        - self.name.isalnum()
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def __eq__(self, other) -> bool:
        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()


class Province(Location):
    """
    A class that represents a province in a country.

    Instance Attributes:
        - name: A string that represents the name of this province.
        - country: A Country object that represents the country of this province.
    """

    country: Country

    def __init__(self, name: str, country: Country) -> None:
        super().__init__(name)
        self.country = country

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.country == other.country

    def __hash__(self) -> int:
        return super().__hash__()


class BaseData(object):
    """
    A class that represents the most basic data.
    """

    def __init__(self) -> None:
        super().__init__()


class TimeBasedData(BaseData):
    """
    A class that represents the data that is based on date and time.

    Instance Attributes:
        - date: A date object that represent the time of this data.
    """

    date: datetime.date

    def __init__(self, date: datetime.date) -> None:
        super().__init__()
        self.date = date

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.date == other.date


class CovidCaseData(TimeBasedData):
    """
    A class that represents a location's covid cases data at a time.
    
    Instance Attributes:
        - province: The province. None if not applicable.
        - country: The country. None if not applicable (For global data).
        - cases: The number of confirmed COVID-19 cases at this date and location.

    Representation Invariants:
        - self.cases >= 0
    """

    province: Province
    country: Country
    cases: int

    def __init__(self, date: datetime.date, cases: int,
                 country: Country = None, province: Province = None) -> None:
        super().__init__(date)
        self.country = country
        self.cases = cases
        self.province = province

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and \
               self.province == other.province and \
               self.country == other.country and \
               self.cases == other.cases

    def __str__(self) -> str:
        return f'{self.cases} cases in {self.province} {self.country} ' \
               f'at {str(self.date)}'


class SchoolClosureData(TimeBasedData):
    """
    A class that stores the closure state of schools in a country at a time.
    
    Instance Attributes:
        - country: The country. Should not be None for our project.
        - status: The closure status specified by enum class ClosureStatus.
    """

    country: Country
    status: ClosureStatus

    def __init__(self, date: datetime.date, status: ClosureStatus, country: Country = None):
        super().__init__(date)
        self.country = country
        self.status = status

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and \
               self.country == other.country and \
               self.status == other.status

    def __str__(self) -> str:
        return f'Schools {self.status} in {self.country} at {self.date}'


# =================================================================================================
# Constants
# =================================================================================================

# =================================================================================================
# COVID 19
# All covid cases from our datasets.
ALL_COVID_CASES: List[CovidCaseData] = []
COUNTRIES_TO_ALL_COVID_CASES: Dict[Country, List[CovidCaseData]] = {}

# The covid cases of the whole country, excluding provinces and cities.
COUNTRIES_TO_COVID_CASES: Dict[Country, List[CovidCaseData]] = {}

# Global covid cases (whole earth)
GLOBAL_COVID_CASES: List[CovidCaseData] = []

# =================================================================================================
# School closures
# All school closures from our datasets.
ALL_SCHOOL_CLOSURES: List[SchoolClosureData] = []

COUNTRIES_TO_SCHOOL_CLOSURES: Dict[Country, List[SchoolClosureData]] = {}

GLOBAL_SCHOOL_CLOSURES: List[SchoolClosureData] = []

# =================================================================================================
# Locations
# All countries from our datasets.
COUNTRIES: Set[Country] = set()
SORTED_COUNTRIES: List[Country] = []
KEY_COUNTRIES: List[Country] = [
    Country('China'),
    Country('US'),
    Country('Canada'),
    Country('Russia'),
    Country('United Kingdom'),
    Country('France'),
]

# All provinces from our datasets.
PROVINCES: Set[Province] = set()
SORTED_PROVINCES: List[Province] = []
COUNTRIES_TO_PROVINCES: Dict[Country, List[Province]] = {}

# =================================================================================================
# Mappings
# Status correspond to the raw school closure data set.
STATUS_DICT = {
    'Fully open'            : ClosureStatus.FULLY_OPEN,
    'Partially open'        : ClosureStatus.PARTIALLY_OPEN,
    'Closed due to COVID-19': ClosureStatus.CLOSED,
    'Academic break'        : ClosureStatus.ACADEMIC_BREAK
}

ENUM_TO_STATUS_DICT = {
    ClosureStatus.ACADEMIC_BREAK: 'Academic break',
    ClosureStatus.FULLY_OPEN    : 'Fully open',
    ClosureStatus.PARTIALLY_OPEN: 'Partially open',
    ClosureStatus.CLOSED        : 'Closed due to COVID-19'
}

# Country names in the closure data set will be replaced by the value.
CLOSURE_COUNTRY_NAMES_FIX: Dict[str, str] = {
    'Bolivia (Plurinational State of)'                    : 'Bolivia',
    'Brunei Darussalam'                                   : 'Brunei',
    'Central African republic'                            : 'Central African Republic',
    'Congo'                                               : 'Congo (Brazzaville)',
    'Democratic Republic of the Congo'                    : 'Congo (Kinshasa)',
    'Iran (Islamic Republic of)'                          : 'Iran',
    'Republic of Korea'                                   : 'Korea, South',
    'Lao PDR'                                             : 'Laos',
    'Micronesia (Federated States of)'                    : 'Micronesia',
    'Republic of Moldova'                                 : 'Moldova',
    'Russian Federation'                                  : 'Russia',
    'Syrian Arab Republic'                                : 'Syria',
    'United Republic of Tanzania'                         : 'Tanzania',
    'United States of America'                            : 'US',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
    'Viet Nam'                                            : 'Vietnam'
}

# "Country" names in the covid data set that will be deleted.
COVID_COUNTRIES_DELETE: Set[str] = {
    'Burma',
    'Diamond Princess',
    'Holy See',
    'Kosovo',
    'MS Zaandam',
    'Sao Tome and Principe',
    'Summer Olympics 2020',
    'Taiwan*',
    'West Bank and Gaza'
}

# Country names in the closure data set that will be deleted.
CLOSURE_COUNTRIES_DELETE: Set[str] = {
    'Anguilla',
    'Aruba',
    'Bermuda',
    'British Virgin Islands',
    'Cayman Islands',
    'Cook Islands',
    "Democratic People's Republic of Korea",
    'Faroe Islands',
    'Gibraltar',
    'Greenland',
    'Montserrat',
    'Myanmar',
    'Nauru',
    'Niue',
    'Palestine',
    'Sint Marteen',
    'Svalbard',
    'Tokelau',
    'Turkmenistan',
    'Turks and Caicos Island',
    'Tuvalu'
}

# len(ALL_COVID_CASES) + len(ALL_SCHOOL_CLOSURES)
TOTAL_NUMBER_DATA = 304410
# TOTAL_NUMBER_DATA + data manipulation + download datasets
TOTAL_PROGRESS = TOTAL_NUMBER_DATA + \
                 math.ceil(TOTAL_NUMBER_DATA * 0.01) + \
                 math.ceil(TOTAL_NUMBER_DATA * 0.01) + \
                 math.ceil(TOTAL_NUMBER_DATA * 0.01)

# The current progress and its description
progress = 0
progress_description = ''


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

def init_data() -> None:
    """Read and process all data needed."""
    import time
    timestamp1 = time.time()

    global progress
    global progress_description

    progress_description = 'Checking and downloading resources...'
    try:
        resource_manager.init_resources()
    except resource_manager.FailedToDownloadResourceException as e:
        progress_description = str(e)
        return
    progress += math.ceil(TOTAL_NUMBER_DATA * 0.01)

    logging.info('Initializing data...')

    progress_description = 'Reading data...'
    read_covid_data_global(
            'resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
    read_closure_data('resources/school_closures_datasets/full_dataset_31_oct.csv')

    progress_description = 'Manipulating data...'
    # Init locations
    SORTED_COUNTRIES.extend(settings.sort([c for c in COUNTRIES],
                                          compare=lambda c1, c2: 1 if c1.name > c2.name else -1))
    SORTED_PROVINCES.extend(settings.sort([p for p in PROVINCES],
                                          compare=lambda p1, p2: 1 if p1.name > p2.name else -1))

    global COUNTRIES_TO_PROVINCES
    COUNTRIES_TO_PROVINCES = algorithms.group(SORTED_PROVINCES, lambda p: p.country)

    # Init covid cases
    global COUNTRIES_TO_ALL_COVID_CASES
    COUNTRIES_TO_ALL_COVID_CASES = algorithms.group(ALL_COVID_CASES, lambda c: c.country)
    global COUNTRIES_TO_COVID_CASES
    COUNTRIES_TO_COVID_CASES = {k: algorithms.linear_predicate(
            COUNTRIES_TO_ALL_COVID_CASES[k], lambda c: c.province is None
    ) for k in COUNTRIES_TO_ALL_COVID_CASES}
    # Special cases: Canada, China, and Australia
    specials = ['China', 'Canada', 'Australia']
    for country_name in specials:
        country = Country(country_name)
        COUNTRIES_TO_COVID_CASES[country] = calculate_country_total_covid_cases(country)
    # Global covid cases (No country, whole earth)
    init_global_total_covid_cases()
    progress += math.ceil(TOTAL_NUMBER_DATA * 0.01)

    # Init school closures
    global COUNTRIES_TO_SCHOOL_CLOSURES
    COUNTRIES_TO_SCHOOL_CLOSURES = algorithms.group(ALL_SCHOOL_CLOSURES, lambda c: c.country)
    init_global_school_closures()
    progress += math.ceil(TOTAL_NUMBER_DATA * 0.01)

    timestamp2 = time.time()
    seconds_elapsed = round(timestamp2 - timestamp1, 3)
    progress_description = f'Ready in {seconds_elapsed} seconds!'
    logging.info(f'Successfully initialized all data in '
                 f'{seconds_elapsed} seconds!')


def reset_data() -> None:
    """
    Reset all constants to their default status.
    """
    ALL_COVID_CASES.clear()
    COUNTRIES_TO_ALL_COVID_CASES.clear()
    COUNTRIES_TO_COVID_CASES.clear()
    GLOBAL_COVID_CASES.clear()
    ALL_SCHOOL_CLOSURES.clear()
    COUNTRIES_TO_SCHOOL_CLOSURES.clear()
    GLOBAL_SCHOOL_CLOSURES.clear()
    COUNTRIES.clear()
    SORTED_COUNTRIES.clear()
    PROVINCES.clear()
    SORTED_PROVINCES.clear()
    COUNTRIES_TO_PROVINCES.clear()
    global progress
    progress = 0
    global progress_description
    progress_description = ''


def get_progress() -> tuple[float, str]:
    """Return the current progress divided by the total progress"""
    return progress / TOTAL_PROGRESS, progress_description


def init_global_school_closures() -> None:
    """
    Initialize the global variable GLOBAL_SCHOOL_CLOSURES.

    Basically, this function calculates the total school closures for every country on a day
    and choose the status with the greatest number of schools as the status for that day.
    """
    global GLOBAL_SCHOOL_CLOSURES
    current_date = ALL_SCHOOL_CLOSURES[0].date
    num_of_status = {
        ClosureStatus.CLOSED        : 0,
        ClosureStatus.FULLY_OPEN    : 0,
        ClosureStatus.ACADEMIC_BREAK: 0,
        ClosureStatus.PARTIALLY_OPEN: 0
    }
    for closure in ALL_SCHOOL_CLOSURES:
        if current_date == closure.date:
            num_of_status[closure.status] += 1
        else:
            keys = [k for k in num_of_status]
            values = [num_of_status[k] for k in keys]
            index = values.index(max(values))
            GLOBAL_SCHOOL_CLOSURES.append(SchoolClosureData(current_date, keys[index]))
            current_date = closure.date
            for k in num_of_status:
                num_of_status[k] = 0


def calculate_country_total_covid_cases(country: Country) -> List[CovidCaseData]:
    """
    Return a List containing the total covid cases of the given country.
    The covid cases of the given country were previously separated by provinces.
    
    Preconditions:
        - country in COUNTRIES_TO_ALL_COVID_CASES
        - country in COUNTRIES_TO_PROVINCES
    """
    cases = COUNTRIES_TO_ALL_COVID_CASES[country]
    result: List[CovidCaseData] = []
    current_province = cases[0].province
    index = 0
    num_provinces = len(COUNTRIES_TO_PROVINCES[country])
    for i, case in enumerate(cases):
        if case.province != current_province:
            index = i
            break
        result.append(CovidCaseData(case.date, case.cases, case.country))

    for i in range(2, num_provinces):
        for j in range(index):
            result[j].cases += cases[i * index + j].cases

    return result


def init_global_total_covid_cases() -> None:
    """
    Initialize the global variable GLOBAL_COVID_CASES.

    Basically, this function calculates the total cases by summing up all cases for all countries
    on a day, and then append the total covid cases on that day to GLOBAL_COVID_CASES.
    """
    global GLOBAL_COVID_CASES
    GLOBAL_COVID_CASES.extend(CovidCaseData(c.date, 0)
                              for c in COUNTRIES_TO_COVID_CASES[Country('China')])
    for country in COUNTRIES_TO_COVID_CASES:
        for i, case in enumerate(COUNTRIES_TO_COVID_CASES[country]):
            GLOBAL_COVID_CASES[i].cases += case.cases


def read_covid_data_global(filename: str) -> None:
    """
    Read the resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv
    into ALL_COVID_CASES.
    """
    with open(filename) as file:
        reader = csv.reader(file)

        # Reads the first line header of the given file
        header = next(reader)

        for row in reader:
            country = Country(row[1])
            province = Province(row[0], country)

            if not is_in_ascii(country.name) or country.name in COVID_COUNTRIES_DELETE:
                continue

            COUNTRIES.add(country)

            if province.name != '':
                PROVINCES.add(province)
            else:
                province = None

            for i in range(4, len(header)):
                raw_date = header[i].split('/')
                d = datetime.date(year=int(f'20{raw_date[2]}'),
                                  month=int(raw_date[0]),
                                  day=int(raw_date[1])
                                  )

                ALL_COVID_CASES.append(CovidCaseData(date=d,
                                                     country=country,
                                                     cases=int(row[i]),
                                                     province=province))
                global progress
                progress += 1


def read_closure_data(filename: str) -> None:
    """
    Read the resources/school_closures_datasets/full_dataset_31_oct.csv
    into ALL_SCHOOL_CLOSURES
    """
    with open(filename) as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            country_name = row[2]

            if not is_in_ascii(country_name) or country_name in CLOSURE_COUNTRIES_DELETE:
                continue

            if country_name in CLOSURE_COUNTRY_NAMES_FIX:
                country_name = CLOSURE_COUNTRY_NAMES_FIX[country_name]

            day, month, year = row[0].split('/')
            ALL_SCHOOL_CLOSURES.append(SchoolClosureData(date=datetime.date(year=int(year),
                                                                            month=int(month),
                                                                            day=int(day)),
                                                         country=Country(country_name),
                                                         status=STATUS_DICT[row[3]]))
            global progress
            progress += 1


def is_in_ascii(s: str) -> bool:
    """Returns whether all the characters in string s is in the ASCII Table or not.

    >>> is_in_ascii('Curaçao')
    False

    >>> is_in_ascii('Scott')
    True
    """

    return all(ord(char) < 128 for char in s)
