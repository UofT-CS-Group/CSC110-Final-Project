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

# =================================================================================================
# Constants
# =================================================================================================

COVID19_RESOURCE_NAME = 'time_series_covid19_confirmed_global.csv'
SCHOOL_CLOSURE_RESOURCE_NAME = 'full_dataset_31_oct.csv'
ICON_RESOURCE_NAME = 'icon.png'
MARKERS_ICON_RESOURCE_NAMES = ['m00.webp', 'm01.webp', 'm02.webp', 'm03.webp', 'm04.webp',
                               'm05.webp', 'm06.webp', 'm07.webp', 'm08.webp', 'm09.webp',
                               'm10.webp', 'm11.webp', 'm12.webp', 'm13.webp', 'm14.webp',
                               'm15.webp', 'm16.webp', 'm17.webp', 'm18.webp', 'm19.webp',
                               'm20.webp', 'm21.webp', 'm22.webp', 'm23.webp', 'm24.webp',
                               'm25.webp', 'm26.webp', 'm27.webp', 'm28.webp', 'm29.webp',
                               'm30.webp', 'm31.webp', 'm32.webp', 'm33.webp', 'm34.webp',
                               'm35.webp', 'm36.webp']
MARKERS_ICON_RESOURCE_MD5S = \
    ['2516b9b9478445f0aa2f343b693287d2', '08a671c63e0a486dd66490cd8031c096',
     '649d76bf9be016809e334c2f0a28051b', '28e5855bbef8d03befcf3e6680aa4fb2',
     'c4800af014e4781e87925a70e4fef478', 'ca6f7c7784c3657b353d64f8e7e23324',
     'f1adecca8f29f1023a05385e7dcc674f', '27f512a1b41b405f6bf4d24c160a9a85',
     '41b09848a24c02bb0e42696fd923cbf3', '55c33bacbf033b5a28c3b88bc340a164',
     '8a2d1248f6b9650771e53df983f4922a', '3da43c3943e0fd35f2b5e60730ff10ee',
     '43b13e75eb87111eb8297752b4c8fd5d', 'e63f8d4362a2f9fe375f7241ee590287',
     '0bafbee3bccc60b539d6cd36d5d291ea', 'c917adeefca067f0dba6d037188af9cc',
     '4fc4ba80d1b36d0ffb5ed4b1fefa3ff0', '9030d1476cdcc6c2c4c1e61520b2a527',
     'fb136919c9f332b444086f0612f0bad6', 'd643aa5dec07341a2d5c30897272d123',
     '365454729acc0a355cba59fba0e1e12b', 'a873cfeee199064b3a851b1c971d02f7',
     '48fe997cd5f335d7f7d21df13cd811cb', 'e6398c2cc007443ffb4642615b4ee42b',
     'ce059d192da59e4394327120e9165a51', '10d8dbc0551ad359abb756a3abc5de50',
     '6dd7de7405c6fcf2b82b83669017c6c0', 'cbf1103fa8626e91afcb2032ea105c35',
     '89d9475114f803352767d0c91894c8b6', '3cf4679564ed8ed4b3690960685cb8f9',
     '278edd692efdd27c7ee5ffd731018e73', '2004bb108397a867958b4ca3eaf32f92',
     'aee8ea41f6f605fb69aeff7cdfc4c87d', '3f54840423cbbfa01b2e7d8160beee5a',
     '7d6d3496029fa7a87d69a36794193df4', 'fa3439c417d310e28210d9bbc3450a15',
     '8cdda7e121352625ec963f37bcdd5427']

# MD5 Checksum Settings
BUFFER_SIZE = 65536
# Number of attempts to re-download file if failed
RETRY_COUNT = 3


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
    covid19_url = 'https://raw.githubusercontent.com/UofT-CS-Group/CSC110-Final-Project/main/' \
                  'Application/resources/covid_cases_datasets/' \
                  'time_series_covid19_confirmed_global.csv'
    closure_url = 'https://raw.githubusercontent.com/UofT-CS-Group/CSC110-Final-Project/main/' \
                  'Application/resources/school_closures_datasets/full_dataset_31_oct.csv'
    icon_url = 'https://raw.githubusercontent.com/UofT-CS-Group/CSC110-Final-Project/main/' \
               'Application/resources/assets/icon.png'

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
