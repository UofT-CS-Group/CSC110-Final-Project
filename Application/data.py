"""
CSC110 Final Project - Data Classes File

Contains functions to read Raw CSV File that has the specified format
"""

from typing import List, Set
from enum import Enum
import datetime
import csv


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
    
    def __eq__(self, other):
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
    
    def __eq__(self, other):
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
    
    def __eq__(self, other):
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
    
    def __init__(self, date: datetime.date):
        super().__init__()
        self.date = date
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.date == other.date


class CovidCaseData(TimeBasedData):
    """ A class that represents a location's covid cases data at a time.
    
    Instance Attributes:
        - city: The city. None if not applicable.
        - province: The province. None if not applicable.
        - country: The country. Should not be None for our project.
        - cases: The number of confirmed COVID-19 cases at this date and location.

    Representation Invariants:
        - self.cases >= 0
    """
    
    city: City
    province: Province
    country: Country
    cases: int
    
    def __init__(self, date: datetime.date, country: Country, cases: int,
                 city: City = None, province: Province = None):
        super().__init__(date)
        self.country = country
        self.cases = cases
        self.city = city
        self.province = province
    
    def __eq__(self, other):
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
    
    def __init__(self, date: datetime.date, country: Country, status: ClosureStatus):
        super().__init__(date)
        self.country = country
        self.status = status
    
    def __eq__(self, other):
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

# All school closures from our datasets.
ALL_SCHOOL_CLOSURES: List[SchoolClosureData] = []

# All countries from our datasets.
COUNTRIES: Set[Country] = set()

# All provinces from our datasets.
PROVINCES: Set[Province] = set()

# All cities from our datasets.
# Should contain only US cities.
CITIES: Set[City] = set()


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

def init_data() -> None:
    """Read and process all data needed."""
    import time
    timestamp1 = time.time()
    
    read_covid_data('resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv')
    read_covid_data('resources/covid_cases_datasets/time_series_covid19_confirmed_US.csv')
    read_closure_data('resources/school_closures_datasets/full_dataset_31_oct.csv')
    
    ALL_COVID_CASES.sort(key=lambda c: c.date)
    ALL_SCHOOL_CLOSURES.sort(key=lambda c: c.date, reverse=True)
    
    timestamp2 = time.time()
    print(f'Successfully initialize all data in {timestamp2 - timestamp1} seconds!')


def read_covid_data(filename: str) -> None:
    """Reads a CSV file at location filename, then append the results into the ALL_COVID_CASES
    variable as a CovidCaseData object

    Preconditions:
        - The CSV File must contain the specified headers ('province', 'country', '1/22/20')
        - No duplicated header column of the same identifier
    """
    
    with open(filename) as file:
        reader = csv.reader(file)
        
        # Reads the first line header of the given file
        header = next(reader)
        
        # Special treatment for US Covid Dataset
        if header[5] == 'Admin2':
            header[5] = 'city'
        
        # Converts anything in our header row to lower case, so we don't need the headers to be
        # exactly the same as what we expect
        header = [item.lower() for item in header]
        
        # Extend the result list to our ALL_COVID_CASES global variable
        for row in reader:
            covid_obs = process_row_covid(header, row)
            
            # Used covid_obs[0] because the whole list contains data with the same country
            if is_in_ascii(covid_obs[0].country.name):
                ALL_COVID_CASES.extend(process_row_covid(header, row))


def read_closure_data(filename: str) -> None:
    """Reads a CSV file at location filename, then append the results to the ALL_SCHOOL_CLOSURES
    variable as a SchoolClosureData object

    Preconditions:
        - The CSV File must contain the specified headers ('date', 'iso', 'country', 'status')
        - No duplicated header column of the same identifier
    """
    
    with open(filename) as file:
        reader = csv.reader(file)
        
        next(reader)
        
        for row in reader:
            closure_obs = process_row_closure(row)
            
            if is_in_ascii(closure_obs.country.name):
                ALL_SCHOOL_CLOSURES.append(process_row_closure(row))


def process_row_covid(header: List[str], row: List[str]) -> List[CovidCaseData]:
    """Process a row of COVID Data into a list of CovidCaseData, as a row contains multiple
    CovidCaseDatas

    Preconditions:
        - The CSV File must contain the specified headers ('province', 'country', '1/22/20')
        - Date must be given in the format 'mm/dd/yy'
    """
    
    start_date_index = header.index('1/22/20')
    
    country = None
    province = None
    city = None
    
    for i in range(start_date_index):
        
        if 'country' in header[i]:
            country = Country(row[i])
        elif 'province' in header[i]:
            province = Province(row[i], country)
        elif 'city' in header[i]:
            city = City(row[i], province)
    
    if province is not None and province.name != '':
        province.country = country
        PROVINCES.add(province)
    
    if city is not None and city.name != '':
        city.province = province
        CITIES.add(city)
    
    COUNTRIES.add(country)
    
    result = []
    
    for i in range(start_date_index, len(header)):
        raw_date = header[i].split('/')
        d = datetime.date(year=int(f'20{raw_date[2]}'),
                          month=int(raw_date[0]),
                          day=int(raw_date[1])
                          )
        
        result.append(CovidCaseData(date=d,
                                    country=country,
                                    cases=int(row[i]),
                                    city=city,
                                    province=province))
    
    return result


STATUS_DICT = {'Fully open'            : ClosureStatus.FULLY_OPEN,
               'Partially open'        : ClosureStatus.PARTIALLY_OPEN,
               'Closed due to COVID-19': ClosureStatus.CLOSED,
               'Academic break'        : ClosureStatus.ACADEMIC_BREAK
               }


def process_row_closure(row: List[str]) -> SchoolClosureData:
    """Process a row of Closure Data into a single SchoolClosureData, as a row contains
    one entry

    Preconditions:
        - The CSV File must contain the specified headers ('date', 'iso', 'country', 'status')
        - Date must be given in the format 'dd/mm/yyyy'
    """
    
    country = Country(name=row[2])
    COUNTRIES.add(country)
    
    day, month, year = row[0].split('/')
    
    return SchoolClosureData(date=datetime.date(year=int(year),
                                                month=int(month),
                                                day=int(day)),
                             country=country,
                             status=STATUS_DICT[row[3]])


def is_in_ascii(s: str) -> bool:
    """Returns whether all the characters in string s is in the ASCII Table or not

    >>> is_in_ascii('Curaçao')
    False

    >>> is_in_ascii('Scott')
    True
    """
    
    return all(ord(char) < 128 for char in s)
