from typing import List
from datetime import datetime
from enum import Enum


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
        - name: A string that represents the name of this province.
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
    """ A class that represents the data that based on date and time.

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

ALL_SCHOOL_CLOSURES: List[SchoolClosureData]

# =================================================================================================
# Functions
# Read raw data into ALL_COVID_CASES and ALL_SCHOOL_CLOSURES.
# =================================================================================================
