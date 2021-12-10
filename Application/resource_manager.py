"""
The module contains functions and classes for downloading and checking resources.
"""
# Future features
from __future__ import annotations

# Python built-ins
import hashlib
import json
import logging
import os
from typing import Dict, Optional

# Requests library
import requests

# =================================================================================================
# Constants
# =================================================================================================

# These are all preferred names.
COVID19_RESOURCE_NAME = 'covid'
SCHOOL_CLOSURE_RESOURCE_NAME = 'closure'
ICON_RESOURCE_NAME = 'icon'
MARKERS_ICON_RESOURCE_NAMES = ['m00.webp', 'm01.webp', 'm02.webp', 'm03.webp', 'm04.webp',
                               'm05.webp', 'm06.webp', 'm07.webp', 'm08.webp', 'm09.webp',
                               'm10.webp', 'm11.webp', 'm12.webp', 'm13.webp', 'm14.webp',
                               'm15.webp', 'm16.webp', 'm17.webp', 'm18.webp', 'm19.webp',
                               'm20.webp', 'm21.webp', 'm22.webp', 'm23.webp', 'm24.webp',
                               'm25.webp', 'm26.webp', 'm27.webp', 'm28.webp', 'm29.webp',
                               'm30.webp', 'm31.webp', 'm32.webp', 'm33.webp', 'm34.webp',
                               'm35.webp', 'm36.webp']

# MD5 Checksum Settings, it will be updated by the config file
BUFFER_SIZE = 65536
# Number of attempts to re-download file if failed, it will be updated by the config file
RETRY_COUNT = 3


# =================================================================================================
# Classes
# =================================================================================================

class Config(object):
    """
    A class represents a read-only json config.

    >>> config = Config('config.json')
    >>> config['setting']
    A dict.
    """

    file_path: str
    config_dict: Dict

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        with open(self.file_path, "rb") as file:
            self.config_dict = json.loads(file.read())

    def __getitem__(self, item):
        return self.config_dict[item]


class Resource(object):
    """
    This class represents a resource that have both local and remote path.

    Instance Attributes:
        - name: The local file name of the resource with extension.
        - preferred_name: The preferred name of this resource.
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
    preferred_name: str
    local_dir_path: str
    local_path: str
    remote_path: str
    identifier_expected: str
    identifier_actual: Optional[str]
    is_init: bool = False

    def __init__(self, name: str, local_path: str, remote_path: str,
                 identifier_expected: str, preferred_name: str = None) -> None:
        self.name = name
        self.local_path = local_path
        self.remote_path = remote_path
        self.identifier_expected = identifier_expected
        self.identifier_actual = None
        self.local_dir_path = self.local_path[:-len(self.name) - 1]
        self.preferred_name = preferred_name if preferred_name is not None else self.name

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

    def to_dict(self) -> Dict:
        return {
            'preferred_name': self.preferred_name,
            'name'          : self.name,
            'local_path'    : self.local_path,
            'remote_path'   : self.remote_path,
            'identifier'    : self.identifier_expected
        }

    @classmethod
    def from_dict(cls, source: Dict) -> Resource:
        return cls(source['name'],
                   source['local_path'],
                   source['remote_path'],
                   source['identifier'],
                   source['preferred_name']
                   )

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
    if resource.is_init:
        return True
    if resource.is_complete():
        return True
    else:
        # Although we may fail to download the resource, it is still "initialized."
        resource.is_init = True
        for i in range(RETRY_COUNT):
            resource.download()
            resource.generate_identifier()
            if resource.is_complete():
                return True
            logging.error(f'Failed to download {resource.name} {i + 1} times! Retrying...')
    return False


def register_resources(resource_config: Dict) -> None:
    """
    Register all resources needed.
    """
    global BUFFER_SIZE
    BUFFER_SIZE = resource_config['buffer_size']
    global RETRY_COUNT
    RETRY_COUNT = resource_config['retry_count']

    resources = resource_config['resources']
    for raw_resource in resources:
        RESOURCES_DICT[raw_resource['preferred_name']] = Resource.from_dict(raw_resource)


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
