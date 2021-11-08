"""
CSC110 Final Project - Data Classes File

Contains functions to read Raw CSV File that has the specified format
"""

from typing import List
from datetime import datetime
from enum import Enum
import csv
import string


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


class Country(Location):
    """ A class that represents a country in the world.
    
    Instance Attributes:
        - name: A string that represents the name of this country.
        - iso_code: A length-3 string that represents the ISO code of this country.

    Representation Invariants:
        - self.name.isalnum()
    """
    
    iso_code: str
    
    def __init__(self, name: str, iso_code: str) -> None:
        super().__init__(name)
        self.iso_code = iso_code
    
    def __eq__(self, other):
        return super().__eq__(other)


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
    
    date: datetime
    
    def __init__(self, date: datetime):
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
    
    def __init__(self, date: datetime, country: Country, cases: int,
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


class SchoolClosureData(TimeBasedData):
    """ A class that stores the closure state of schools in a country at a time.
    
    Instance Attributes:
        - country: The country. Should not be None for our project.
        - status: The closure status specified by enum class ClosureStatus.
    """
    
    country: Country
    status: ClosureStatus
    
    def __init__(self, date: datetime, country: Country, status: ClosureStatus):
        super().__init__(date)
        self.country = country
        self.status = status
    
    def __eq__(self, other):
        return super().__eq__(other) and \
               self.country == other.country and \
               self.status == other.status


# =================================================================================================
# Constants
# =================================================================================================

ALL_COVID_CASES: List[CovidCaseData]
ALL_COVID_CASES = []

ALL_SCHOOL_CLOSURES: List[SchoolClosureData]
ALL_SCHOOL_CLOSURES = []

ASCII_TABLE = string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.digits


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

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
        if header[3] == 'Admin2':
            header[3] = 'City'

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

        header = next(reader)

        header = [item.lower() for item in header]

        for row in reader:
            closure_obs = process_row_closure(header, row)

            if is_in_ascii(closure_obs.country.name):
                ALL_SCHOOL_CLOSURES.append(process_row_closure(header, row))


def process_row_covid(header: List[str], row: List[str]) -> List[CovidCaseData]:
    """Process a row of COVID Data into a list of CovidCaseData, as a row contains multiple
    CovidCaseDatas

    Preconditions:
        - The CSV File must contain the specified headers ('province', 'country', '1/22/20')
        - Date must be given in the format 'mm/dd/yy'
    """
    province_index = ['province' in s for s in header].index(True)
    country_index = ['country' in s for s in header].index(True)

    # Attempts to obtain the city and iso code
    try:
        city_index = ['city' in s for s in header].index(True)
        iso_index = ['iso' in s for s in header].index(True)

        country = Country(name=row[country_index], iso_code=row[iso_index])
        province = Province(name=row[province_index], country=country)
        city = City(name=row[city_index], province=province)

    # If an error is raised, no such value exists, so we will default them to an empty string
    except ValueError:
        country = Country(name=row[country_index], iso_code='')
        province = Province(name=row[province_index], country=country)
        city = City(name='', province=province)

    # Assumes that the data's first entry is at January 22, 2020
    start_date_index = header.index('1/22/20')
    end_date_index = len(header)

    return [CovidCaseData(country=country,
                          province=province,
                          city=city,
                          date=datetime(year=int('20' + header[date].split('/')[2]),
                                        month=int(header[date].split('/')[0]),
                                        day=int(header[date].split('/')[1])),
                          cases=int(row[date]))
            for date in range(start_date_index, end_date_index)]


def process_row_closure(header: List[str], row: List[str]) -> SchoolClosureData:
    """Process a row of Closure Data into a single SchoolClosureData, as a row contains
    one entry

    Preconditions:
        - The CSV File must contain the specified headers ('date', 'iso', 'country', 'status')
        - Date must be given in the format 'dd/mm/yyyy'
    """

    date_index = ['date' in s for s in header].index(True)
    iso_index = ['iso' in s for s in header].index(True)
    country_index = ['country' in s for s in header].index(True)
    status_index = ['status' in s for s in header].index(True)

    country = Country(name=row[country_index],
                      iso_code=row[iso_index])

    day, month, year = row[date_index].split('/')

    # Parse the status so that it is all lower case
    row[status_index] = row[status_index].lower()

    status_dict = {'fully open': ClosureStatus.FULLY_OPEN,
                   'partially open': ClosureStatus.PARTIALLY_OPEN,
                   'closed due to covid-19': ClosureStatus.CLOSED,
                   'academic break': ClosureStatus.ACADEMIC_BREAK}

    return SchoolClosureData(date=datetime(year=int(year),
                                           month=int(month),
                                           day=int(day)),
                             country=country,
                             status=status_dict[row[status_index]])


def is_in_ascii(s: str) -> bool:
    """Returns whether all the characters in string s is in the ASCII Table or not

    >>> is_in_ascii('Curaçao')
    False

    >>> is_in_ascii('Scott')
    True
    """

    return all(char in ASCII_TABLE for char in s)
