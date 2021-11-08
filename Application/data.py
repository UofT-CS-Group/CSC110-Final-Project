"""
CSC110 Final Project - Data Classes File

Contains functions to read Raw CSV File that has the specified format
"""

from typing import List
from datetime import datetime
from enum import Enum
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
        return super().__eq__(other) and \
               isinstance(other, self.__class__) and \
               self.country == other.country


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
        return super().__eq__(other)


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
               isinstance(other, self.__class__) and \
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
               isinstance(other, self.__class__) and \
               self.country == other.country and \
               self.status == other.status


# =================================================================================================
# Constants
# =================================================================================================

ALL_COVID_CASES: List[CovidCaseData]
ALL_COVID_CASES = []

ALL_SCHOOL_CLOSURES: List[SchoolClosureData]
ALL_SCHOOL_CLOSURES = []


# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================

def read_covid_data(filename: str) -> None:
    """Reads a CSV file at location filename, then append the results into the ALL_COVID_CASES
    variable as a Class Object of CovidCaseData

    Preconditions:
        - The CSV File must contain the specified headers ('Province', 'Country', '1/22/20')
    """

    with open(filename) as file:
        reader = csv.reader(file)

        # Reads the first line header of the given file
        header = next(reader)

        # Special treatment for US Covid Dataset
        if header[3] == 'Admin2':
            header[3] = 'City'

        # Extend the result list to our ALL_COVID_CASES global variable
        for row in reader:
            ALL_COVID_CASES.extend(process_row_covid(header, row))


def process_row_covid(header: List[str], row: List[str]) -> List[CovidCaseData]:
    """Process a row of COVID Data into a list of CovidCaseData, as a row contains multiple
    CovidCaseDatas

    Preconditions:
        - The CSV File must contain the specified headers ('Province', 'Country', '1/22/20')
    """
    province_index = ['Province' in s for s in header].index(True)
    country_index = ['Country' in s for s in header].index(True)

    # Attempts to obtain the city and iso code
    try:
        city_index = ['City' in s for s in header].index(True)
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
                          date=datetime(year=int(header[date].split('/')[2]),
                                        month=int(header[date].split('/')[0]),
                                        day=int(header[date].split('/')[1])),
                          cases=int(row[date]))
            for date in range(start_date_index, end_date_index)]
