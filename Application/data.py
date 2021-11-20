"""
CSC110 Final Project - Data Classes File

Contains functions to do all processings with our datasets
Also contains CONSTANTS and classes
"""
import math
from typing import List, Set, Dict
from enum import Enum
import datetime
import csv
import hashlib
import algorithms
import main
import settings
import requests
import os


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
    """ A class that represents a physical location in the world.

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
    """ A class that represents a country in the world.
    
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
    """ A class that represents a province in a country.
    
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


class City(Location):
    """ A class that represents a city in a province.
    
    Instance Attributes:
        - name: A string that represents the name of this city.
        - province: A Province object that represents the province of this city.
    """

    province: Province

    def __init__(self, name: str, province: Province) -> None:
        super().__init__(name)
        self.province = province

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.province == other.province

    def __hash__(self) -> int:
        return super().__hash__()


class BaseData(object):
    """ A class that represents the most basic data.
    """

    def __init__(self) -> None:
        super().__init__()


class TimeBasedData(BaseData):
    """ A class that represents the data that is based on date and time.

    Instance Attributes:
        - date: A datetime object that represent the time of this data.
    """

    date: datetime.date

    def __init__(self, date: datetime.date) -> None:
        super().__init__()
        self.date = date

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.date == other.date


class CovidCaseData(TimeBasedData):
    """ A class that represents a location's covid cases data at a time.
    
    Instance Attributes:
        - city: The city. None if not applicable.
        - province: The province. None if not applicable.
        - country: The country. None if not applicable (For global data).
        - cases: The number of confirmed COVID-19 cases at this date and location.

    Representation Invariants:
        - self.cases >= 0
    """

    city: City
    province: Province
    country: Country
    cases: int

    def __init__(self, date: datetime.date, cases: int,
                 country: Country = None, city: City = None, province: Province = None) -> None:
        super().__init__(date)
        self.country = country
        self.cases = cases
        self.city = city
        self.province = province

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and \
               self.city == other.city and \
               self.province == other.province and \
               self.country == other.country and \
               self.cases == other.cases

    def __str__(self) -> str:
        return f'{self.cases} cases in {self.city} {self.province} {self.country} ' \
               f'at {str(self.date)}'


class SchoolClosureData(TimeBasedData):
    """ A class that stores the closure state of schools in a country at a time.
    
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
# Covid
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

COUNTRIES_TO_ALL_SCHOOL_CLOSURES: Dict[Country, List[SchoolClosureData]] = {}

GLOBAL_SCHOOL_CLOSURES: List[SchoolClosureData] = []

# =================================================================================================
# Locations
# All countries from our datasets.
COUNTRIES: Set[Country] = set()
SORTED_COUNTRIES: List[Country] = []

# All provinces from our datasets.
PROVINCES: Set[Province] = set()
SORTED_PROVINCES: List[Province] = []
COUNTRIES_TO_PROVINCES: Dict[Country, List[Province]] = {}

# All cities from our datasets.
# Should contain only US cities.
CITIES: Set[City] = set()
SORTED_CITIES: List[City] = []
PROVINCES_TO_CITIES: Dict[Province, List[City]] = {}

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
    ClosureStatus.FULLY_OPEN: 'Fully open',
    ClosureStatus.PARTIALLY_OPEN: 'Partially open',
    ClosureStatus.CLOSED: 'Closed due to COVID-19'
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

# Basically len(ALL_COVID_CASES) + len(ALL_SCHOOL_CLOSURES)
TOTAL_NUMBER_DATA = 2470748
TOTAL_PROGRESS = TOTAL_NUMBER_DATA + \
                 math.ceil(TOTAL_NUMBER_DATA * 0.001) + \
                 math.ceil(TOTAL_NUMBER_DATA * 0.001)

# The current progress
progress = 0


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

def md5_hash(filename: str) -> str:
    """
    Return the MD5 hash of the specified filename
    """
    buffer_size = settings.BUFFER_SIZE
    md5 = hashlib.md5()

    with open(filename, 'rb') as file:
        data = file.read(buffer_size)
        while data:
            md5.update(data)
            data = file.read(buffer_size)

    return md5.hexdigest()


def check_files() -> bool:
    """
    Return if we downloaded the right files using the MD5 checksum
    """
    check_covid19_us = md5_hash('resources/covid_cases_datasets/'
                                'time_series_covid19_confirmed_US.csv') == settings.COVID19_US_MD5
    check_covid19_global = md5_hash('resources/covid_cases_datasets/'
                                    'time_series_covid19_confirmed_global.csv'
                                    ) == settings.COVID19_GLOBAL_MD5
    check_closure = md5_hash('resources/school_closures_datasets/'
                             'full_dataset_31_oct.csv') == settings.CLOSURE_MD5

    if not check_covid19_us:
        main.logging.warning('COVID19 US Dataset Checksum failed!')

    if not check_covid19_global:
        main.logging.warning('COVID19 Global Dataset MD5 Checksum failed!')

    if not check_closure:
        main.logging.warning('School Closure Dataset MD5 Checksum failed!')

    return check_covid19_us and check_covid19_global and check_closure


def download_data() -> None:
    """
    Downloads the datasets from our GitHub repository

    This function overwrites whatever files already exist at the specified location

    List of downloads:
        - time_series_covid19_confirmed_global.csv
        - time_series_covid19_confirmed_US.csv
        - full_dataset_31_oct.csv
    """

    os.makedirs('resources/covid_cases_datasets', exist_ok=True)
    os.makedirs('resources/school_closures_datasets', exist_ok=True)
    os.makedirs('resources/assets', exist_ok=True)

    # All URLs contained in settings.py, can be changed anytime
    covid19_us_url = settings.COVID19_US_URL
    covid19_global_url = settings.COVID19_GLOBAL_URL
    closure_url = settings.CLOSURE_URL

    # Downloads the file and writes it in our directories
    try:
        covid19_us_dataset = requests.get(covid19_us_url)
        with open('resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv',
                  'wb') as covid19_us_file:
            covid19_us_file.write(covid19_us_dataset.content)

        covid19_global_dataset = requests.get(covid19_global_url)
        with open('resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv', 'wb')\
                as covid19_global_file:
            covid19_global_file.write(covid19_global_dataset.content)

        closure_dataset = requests.get(closure_url)
        with open('resources/school_closures_datasets/full_dataset_31_oct.csv', 'wb') as closure_file:
            closure_file.write(closure_dataset.content)
    except requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout:
        # Crashes the application's GUI window
        import _thread
        _thread.interrupt_main()

        main.logging.critical('Connection Failed... Aborting application!')
        main.logging.info('Please download the files from settings.py and move them into the resources directory')
        main.logging.info('resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv')
        main.logging.info('resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
        main.logging.info('resources/school_closures_datasets/full_dataset_31_oct.csv')

        raise Exception('Download Failure. Please scroll up to see instructions.')


def init_data() -> None:
    """Read and process all data needed."""
    import time
    timestamp1 = time.time()

    try:
        open('resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv')
        open('resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
        open('resources/school_closures_datasets/full_dataset_31_oct.csv')

    except FileNotFoundError:
        main.logging.warning('Datasets not found! Downloading...')
        download_data()
        main.logging.info('Download success!')

    main.logging.info('Checking completeness of dataset...')

    if not check_files():
        main.logging.warning('MD5 Checksum failed!')
        main.logging.info('Attempting to download original dataset')
        download_data()
        main.logging.info('Download success!')

    # Aborts the application if MD5 Checksum failed twice
    if not check_files():
        main.logging.critical('MD5 Checksum still failed! Aborting.')
        main.logging.info('Perhaps your disk is corrupted?')

        # Crashes the application's GUI window
        import _thread
        _thread.interrupt_main()

    main.logging.info('MD5 Checksum passed!')
    main.logging.info('Initializing data...')

    read_covid_data_global(
            'resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
    read_covid_data_US('resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv')
    read_closure_data('resources/school_closures_datasets/full_dataset_31_oct.csv')

    # Init locations
    SORTED_COUNTRIES.extend(sorted([c for c in COUNTRIES], key=lambda c: c.name))
    SORTED_PROVINCES.extend(sorted([p for p in PROVINCES], key=lambda p: p.name))
    SORTED_CITIES.extend(sorted([c for c in CITIES], key=lambda c: c.name))

    global COUNTRIES_TO_PROVINCES
    COUNTRIES_TO_PROVINCES = algorithms.group(SORTED_PROVINCES, lambda p: p.country)
    global PROVINCES_TO_CITIES
    PROVINCES_TO_CITIES = algorithms.group(SORTED_CITIES, lambda c: c.province)

    global progress

    # Init covid cases
    global COUNTRIES_TO_ALL_COVID_CASES
    COUNTRIES_TO_ALL_COVID_CASES = algorithms.group(ALL_COVID_CASES, lambda c: c.country)
    global COUNTRIES_TO_COVID_CASES
    COUNTRIES_TO_COVID_CASES = {k: algorithms.linear_predicate(
            COUNTRIES_TO_ALL_COVID_CASES[k], lambda c: c.province is None and c.city is None
    ) for k in COUNTRIES_TO_ALL_COVID_CASES}
    # Special cases: Canada, China, and Australia
    specials = ['China', 'Canada', 'Australia']
    for country_name in specials:
        country = Country(country_name)
        COUNTRIES_TO_COVID_CASES[country] = calculate_country_total_covid_cases(country)
    # Global covid cases (No country, whole earth)
    init_global_total_covid_cases()
    progress += math.ceil(TOTAL_NUMBER_DATA * 0.001)

    # Init school closures
    global COUNTRIES_TO_ALL_SCHOOL_CLOSURES
    COUNTRIES_TO_ALL_SCHOOL_CLOSURES = algorithms.group(ALL_SCHOOL_CLOSURES, lambda c: c.country)
    init_global_school_closures()
    progress += math.ceil(TOTAL_NUMBER_DATA * 0.001)

    timestamp2 = time.time()
    main.logging.info(f'Successfully initialized all data in {round(timestamp2 - timestamp1, 2)} seconds!')


def get_progress() -> float:
    """Return the current progress divided by the total progress"""
    return progress / TOTAL_PROGRESS


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
    The covid cases of the given country were previously separated by provinces and (or) cities.
    
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
                                                     city=None,
                                                     province=province))
                global progress
                progress += 1


def read_covid_data_US(filename: str) -> None:
    """
    Read the resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv
    into ALL_COVID_CASES.
    """
    with open(filename) as file:
        reader = csv.reader(file)

        # Reads the first line header of the given file
        header = next(reader)

        for row in reader:
            country = Country(row[7])
            province = Province(row[6], country)
            city = City(row[5], province)

            COUNTRIES.add(country)

            if province.name != '':
                PROVINCES.add(province)
            else:
                province = None

            if city.name != '':
                CITIES.add(city)
            else:
                city = None

            for i in range(11, len(header)):
                raw_date = header[i].split('/')
                d = datetime.date(year=int(f'20{raw_date[2]}'),
                                  month=int(raw_date[0]),
                                  day=int(raw_date[1])
                                  )

                ALL_COVID_CASES.append(CovidCaseData(date=d,
                                                     country=country,
                                                     cases=int(row[i]),
                                                     city=city,
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
