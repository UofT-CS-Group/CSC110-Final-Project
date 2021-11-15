"""
CSC110 Final Project - Data Classes File

Contains functions to read Raw CSV File that has the specified format
"""
from typing import List, Set, Dict
from enum import Enum
import datetime
import csv
import algorithms


# =================================================================================================
# Classes
# =================================================================================================

class ClosureStatus(Enum):
    """ A enum class that represents the closure status of schools.
    
    Note:
        - This class cannot be instantiated.
    """
    
    CLOSED = 0
    PARTIALLY_OPEN = 1
    FULLY_OPEN = 2
    ACADEMIC_BREAK = 3


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
        return f'{self.cases} cases in {self.city} {self.province} {self.country} at {str(self.date)}'


class SchoolClosureData(TimeBasedData):
    """ A class that stores the closure state of schools in a country at a time.
    
    Instance Attributes:
        - country: The country. Should not be None for our project.
        - status: The closure status specified by enum class ClosureStatus.
    """
    
    country: Country
    status: ClosureStatus
    
    def __init__(self, date: datetime.date, country: Country, status: ClosureStatus) -> None:
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

# All covid cases from our datasets.
ALL_COVID_CASES: List[CovidCaseData] = []
COUNTRIES_TO_ALL_COVID_CASES: Dict[Country, List[CovidCaseData]] = {}

# The covid cases of the whole country, excluding provinces and cities.
COUNTRIES_TO_COVID_CASES: Dict[Country, List[CovidCaseData]] = {}

# Global covid cases (whole earth)
GLOBAL_COVID_CASES: List[CovidCaseData] = []

# All school closures from our datasets.
ALL_SCHOOL_CLOSURES: List[SchoolClosureData] = []

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

STATUS_DICT = {'Fully open'            : ClosureStatus.FULLY_OPEN,
               'Partially open'        : ClosureStatus.PARTIALLY_OPEN,
               'Closed due to COVID-19': ClosureStatus.CLOSED,
               'Academic break'        : ClosureStatus.ACADEMIC_BREAK
               }


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

def init_data() -> None:
    """Read and process all data needed."""
    import time
    timestamp1 = time.time()
    
    read_covid_data_global('resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
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
    
    # Init covid cases
    global COUNTRIES_TO_ALL_COVID_CASES
    COUNTRIES_TO_ALL_COVID_CASES = algorithms.group(ALL_COVID_CASES, lambda c: c.country)
    global COUNTRIES_TO_COVID_CASES
    COUNTRIES_TO_COVID_CASES = {k: algorithms.linear_predicate(COUNTRIES_TO_ALL_COVID_CASES[k],
                                                               lambda c: c.province is None and c.city is None)
                                for k in COUNTRIES_TO_ALL_COVID_CASES}
    # Special cases: Canada, China, and Australia
    specials = ['China', 'Canada', 'Australia']
    for country_name in specials:
        country = Country(country_name)
        COUNTRIES_TO_COVID_CASES[country] = calculate_country_total_covid_cases(country)
    # Global covid cases (No country, whole earth)
    calculate_global_total_covid_cases()
    
    timestamp2 = time.time()
    print(f'Successfully initialize all data in {round(timestamp2 - timestamp1, 2)} seconds!')


def calculate_country_total_covid_cases(country: Country) -> List[CovidCaseData]:
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


def calculate_global_total_covid_cases() -> None:
    global GLOBAL_COVID_CASES
    GLOBAL_COVID_CASES.extend(CovidCaseData(c.date, 0) for c in COUNTRIES_TO_COVID_CASES[Country('China')])
    for country in COUNTRIES_TO_COVID_CASES:
        for i, case in enumerate(COUNTRIES_TO_COVID_CASES[country]):
            GLOBAL_COVID_CASES[i].cases += case.cases


def read_covid_data_global(filename: str) -> None:
    with open(filename) as file:
        reader = csv.reader(file)
        
        # Reads the first line header of the given file
        header = next(reader)
        
        for row in reader:
            country = Country(row[1])
            province = Province(row[0], country)
            
            if country.name == '' or not is_in_ascii(country.name):
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


def read_covid_data_US(filename: str) -> None:
    with open(filename) as file:
        reader = csv.reader(file)
        
        # Reads the first line header of the given file
        header = next(reader)
        
        for row in reader:
            country = Country(row[7])
            province = Province(row[6], country)
            city = City(row[5], province)
            
            if country.name == '' or not is_in_ascii(country.name):
                continue
            
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


def read_closure_data(filename: str) -> None:
    with open(filename) as file:
        reader = csv.reader(file)
        
        next(reader)
        
        for row in reader:

            # If we can find a country name that is already in COUNTRIES due to read_covid_data
            # Then, we will actually add the closure data in there.
            # If not, we will skip this closure data.
            if any(c.name in row[2] for c in COUNTRIES):
                countries_list = list(COUNTRIES)

                country_index = [c.name in row[2] for c in countries_list].index(True)
                country = countries_list[country_index]

            else:
                continue

            if not is_in_ascii(country.name):
                continue
            COUNTRIES.add(country)
            day, month, year = row[0].split('/')
            ALL_SCHOOL_CLOSURES.append(SchoolClosureData(date=datetime.date(year=int(year),
                                                                            month=int(month),
                                                                            day=int(day)),
                                                         country=country,
                                                         status=STATUS_DICT[row[3]]))


def is_in_ascii(s: str) -> bool:
    """Returns whether all the characters in string s is in the ASCII Table or not

    >>> is_in_ascii('Curaçao')
    False

    >>> is_in_ascii('Scott')
    True
    """
    
    return all(ord(char) < 128 for char in s)
