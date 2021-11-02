"""
This file contains the function to process the data from the CSV File into different classes.
"""
import csv
import datetime
from typing import Tuple, List
from dataclasses import dataclass


###############################################################################
# Data classes
###############################################################################
@dataclass
class ClosureStatus:
    """A class that records the information of the country (Name and Abbreviation),
    date it was recorded, and the closure status

    Attributes:
        date - The date of which the status was recorded
        abbr - The abbreviation of the Country Name, aka the country code
        country - The name of the country where this status was recorded
        status - The situation of school closure, either Open, Partially open, Closed, or Break
    """
    date: datetime.date
    abbr: str
    country: str
    status: str


@dataclass
class CovidStatus:
    """A class that records the information of the COVID-19 status of a country

    Attributes:
        city - Specifically only in US
        province - The province / state of a given record
        country - The country of a given record
        lat - Latitude of the location of the country
        long - Longitude of the location of the country
        date - The date of the given observation
        case - The number of cumulative cases in this observation
        incr - The number of cases increased since last observation
    """
    city: str
    province: str
    country: str
    lat: float
    long: float
    date: datetime.date
    case: int
    incr: int


###############################################################################
# Functions
###############################################################################
def load_closure_data(filename: str) -> Tuple[List[str], List[ClosureStatus]]:
    """Returns the headers and data stored in filename as a tuple consisting of two elements
    
    The return tuple consists of two elements: 
        - The header row (A list of strings that contains the headers of this data)
        - The data row (A list of ClosureStatus objects)
    """

    with open(filename) as file:
        reader = csv.reader(file)

        header = next(reader)
        data = [process_row_closure(row) for row in reader]

        return header, data


def load_covid_data(filename: str) -> Tuple[List[str], List[CovidStatus]]:
    """Returns the headers and the data stored in the filename as a tuple consisting of two elements

    The return tuple consists of two elements:
        - The header row (A list of strings that contains the header of this CSV File)
        - The data list (A list of CovidStatus objects)

    Data sourced from:
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series

    This function should work for both the US Data and the Global Data
    """
    with open(filename) as file:
        reader = csv.reader(file)

        header = next(reader)

        data = []

        for row in reader:
            data.extend(process_row_covid(header, row))

        return header, data


def process_row_covid(header: List[str], row: List[str]) -> List[CovidStatus]:
    """Converts a row of data into a ClosureStatus object using the header row as indicator

    Preconditions:
        - The row passed in has the format of [Province, Country, Lat, Long, date1, date2, ...]
    """
    # If it is US Dataset, process the header just once
    if header[6] == 'Province_State':

        header[header.index('Province_State')] = 'Province/State'
        header[header.index('Country_Region')] = 'Country/Region'
        header[header.index('Long_')] = 'Long'

    # If it is US Dataset
    if header[0] == 'UID':
        # Set city index and city
        city_index = header.index('Admin2')
        city = row[city_index]

        # Set start date index
        start_date_index = 11

    else:
        # If not US Dataset
        city = 'N/A'
        start_date_index = 4

    province_index = header.index('Province/State')
    country_index = header.index('Country/Region')
    lat_index = header.index('Lat')
    long_index = header.index('Long')

    province = row[province_index]
    country = row[country_index]

    # Taking care of the missing values
    lat = float(row[lat_index]) if row[lat_index] != '' else 0.0
    long = float(row[long_index]) if row[long_index] != '' else 0.0

    return_list = [CovidStatus(city=city,
                               province=province,
                               country=country,
                               lat=lat,
                               long=long,
                               date=datetime.date(month=int(header[date].split('/')[0]),
                                                  day=int(header[date].split('/')[1]),
                                                  year=int(header[date].split('/')[2])),
                               case=int(row[date]),
                               incr=(int(row[date]) - int(row[date - 1])))
                   for date in range(start_date_index + 1, len(row))]

    # Manually append the first day's information in there
    return_list.insert(0, CovidStatus(city=city,
                                      province=province,
                                      country=country,
                                      lat=lat,
                                      long=long,
                                      date=datetime.date(month=int(header[start_date_index].split('/')[0]),
                                                         day=int(header[start_date_index].split('/')[1]),
                                                         year=int(header[start_date_index].split('/')[2])),
                                      case=int(row[start_date_index]),
                                      incr=0))

    return return_list


def process_row_closure(row: List[str]) -> ClosureStatus:
    """Converts a row of data into a ClosureStatus object

    Preconditions:
        - The row passed in has the format of [date, abbr, country, status]
    """
    date_list = row[0].split('/')

    date = datetime.date(day=int(date_list[0]),
                         month=int(date_list[1]),
                         year=int(date_list[2]))

    status_map = {'Fully open': 'Open',
                  'Partially open': 'Partially open',
                  'Closed due to COVID-19': 'Closed',
                  'Academic break': 'Break'}

    return ClosureStatus(date=date,
                         abbr=row[1],
                         country=row[2],
                         status=status_map[row[3]])
