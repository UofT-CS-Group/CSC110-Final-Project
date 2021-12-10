"""
The module contains functions and classes for downloading and checking resources.
"""
# Python built-ins
import hashlib
import logging
import os
from typing import Dict, Optional

# Requests library
import requests

from config_manager import ConfigManager

# =================================================================================================
# Constants
# =================================================================================================

config_manager = ConfigManager("resources/resource.json")
config=config_manager.data

COVID19_RESOURCE_NAME = config["covid_resource_name"]
SCHOOL_CLOSURE_RESOURCE_NAME = config["school_closure_resource_name"]
ICON_RESOURCE_NAME = config["icon_resource_name"]
MARKERS_ICON_RESOURCE_NAMES = config["marker_resource_icon"]["name"]
MARKERS_ICON_RESOURCE_MD5S = config["marker_resource_icon"]["md5"]

# MD5 Checksum Settings
BUFFER_SIZE = config["buffer_size"]
# Number of attempts to re-download file if failed
RETRY_COUNT = config["retry_count"]


# =================================================================================================
# Classes
# =================================================================================================

class Resource(object):
    """
    This class represents a resource that have both local and remote path.

    Instance Attributes:
        - name: The name of the resource. Usually, it is the local file name.
        - local_dir_path: The path of the local directory that contains this resource.
        - local_path: The path of this resource.
        - remote_path: The remote direct url of this resource.
        - identifier_expected: The str expected identifier of this resource.
        - identifier_actual: The actual str identifier of this resource.
            - This could be None.
        - is_init: Whether this resource was initialized before.
            - Note that sometimes although the resource exists locally and valid, is_init may still
              False.
    """
    name: str
    local_dir_path: str
    local_path: str
    remote_path: str
    identifier_expected: str
    identifier_actual: Optional[str]
    is_init: bool = False

    def __init__(self, name: str, local_path: str, remote_path: str,
                 identifier_expected: str) -> None:
        self.name = name
        self.local_path = local_path
        self.remote_path = remote_path
        self.identifier_expected = identifier_expected
        self.identifier_actual = None
        self.local_dir_path = self.local_path[:-len(self.name) - 1]

    def is_complete(self) -> bool:
        """
        Return whether the resource is complete.
        """
        if self.identifier_actual is None:
            try:
                self.generate_identifier()
            except FileNotFoundError:
                logging.error(f'File {self.local_path} not found!')
                return False
        return self.identifier_expected == self.identifier_actual

    def generate_identifier(self) -> None:
        """
        Generate the MD5 hash of this resource and update self.identifier_expected to the
        generated MD5 hash.

        It may raise FileNotFoundError if the local file doesn't exist.
        """
        md5 = hashlib.md5()

        with open(self.local_path, 'rb') as file:
            data = file.read(BUFFER_SIZE)
            while data:
                md5.update(data)
                data = file.read(BUFFER_SIZE)

        self.identifier_actual = md5.hexdigest()

    def download(self) -> bool:
        """
        Try to download the resource specified by remote_path to local_path.
        Return False and print an error message if failed to connect to remote_path.

        Note:
            - This function will create any directories missing.
        """
        logging.info(f'Downloading {self.name}!')
        try:
            remote_resource = requests.get(self.remote_path)
            os.makedirs(self.local_dir_path, exist_ok=True)

            with open(self.local_path, 'wb') as local_resource:
                local_resource.write(remote_resource.content)
                return True

        except requests.exceptions.ConnectionError or requests.exceptions.ConnectTimeout:
            logging.error(f'Failed to connect to {self.remote_path}!')
            return False

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __str__(self) -> str:
        return self.name


class FailedToDownloadResourceException(Exception):

    def __str__(self) -> str:
        return f'Failed to download {self.args[0]}!'


# =================================================================================================
# Other Constants
# =================================================================================================

RESOURCES_DICT: Dict[str, Resource] = {}


# =================================================================================================
# Functions
# =================================================================================================

def init_resources() -> None:
    """
    Download and check all resources needed.

    For each of the resources, the maximum number of attempts to download is specified by
    constants RETRY_COUNT.

    Raise FailedToDownloadResourceException if failed to download any resources.
    """
    for resource_name in RESOURCES_DICT:
        resource = RESOURCES_DICT[resource_name]
        if resource.is_init:
            continue
        is_complete = init_resource(resource)
        if not is_complete:
            logging.error(f'Failed to completely download resource {resource.name} '
                          f'{RETRY_COUNT} times! Aborting...')
            raise FailedToDownloadResourceException(resource_name)

    logging.info('Successfully initialized all resources!')


def init_resource(resource: Resource) -> bool:
    """
    Return True if the given resource is successfully initialized.
    """
    # Although we may fail to download the resource, it is still "initialized."
    resource.is_init = True
    if resource.is_init:
        return True
    if resource.is_complete():
        return True
    else:
        for i in range(RETRY_COUNT):
            resource.download()
            resource.generate_identifier()
            if resource.is_complete():
                return True
            logging.error(f'Failed to download {resource.name} {i + 1} times! Retrying...')
    return False


def register_resources() -> None:
    """
    Register all resources needed.
    """
    covid19_url = config["covid19_url"]
    closure_url = config["closure_url"]
    icon_url = config["icon_url"]

    RESOURCES_DICT[COVID19_RESOURCE_NAME] = \
        Resource(COVID19_RESOURCE_NAME,
                 'resources/covid_cases_datasets/time_series_covid19_confirmed_global.csv',
                 covid19_url,
                 '6a7680ffa0200328bdd2823dd998c62e')
    RESOURCES_DICT[SCHOOL_CLOSURE_RESOURCE_NAME] = \
        Resource(SCHOOL_CLOSURE_RESOURCE_NAME,
                 'resources/school_closures_datasets/full_dataset_31_oct.csv',
                 closure_url,
                 '9426167fdc1b664da627e74d84328c35')

    # The icon resources below are not required, so if they failed to initialize,
    # the program doesn't stop
    RESOURCES_DICT[ICON_RESOURCE_NAME] = \
        Resource(ICON_RESOURCE_NAME,
                 'resources/assets/icon.png',
                 icon_url,
                 'fe7c8b3bb7ee7dccea8372da9250e414')

    for i, name in enumerate(MARKERS_ICON_RESOURCE_NAMES):
        RESOURCES_DICT[name] = \
            Resource(name, f'resources/assets/markers/{name}',
                     f'https://raw.githubusercontent.com/UofT-CS-Group/CSC110-Final-Project/main/'
                     f'Application/resources/assets/markers/{name}',
                     MARKERS_ICON_RESOURCE_MD5S[i])


def md5_hash(local_path: str) -> str:
    """
    Return the MD5 hash of the specified filename.
    This is a helper function.
    """
    md5 = hashlib.md5()

    with open(local_path, 'rb') as file:
        data = file.read(BUFFER_SIZE)
        while data:
            md5.update(data)
            data = file.read(BUFFER_SIZE)

    return md5.hexdigest()
