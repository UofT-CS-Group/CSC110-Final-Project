"""
A config manager used to process the file IO.
"""
import os, json


class ConfigManager:
    """
    Used for config IO.
    """
    def __init__(self, filename) -> None:
        """
        Initialize the file name and check whether the config file exists or not.
        """
        self.filename = filename
        if not os.path.isfile(self.filename):
            raise FileNotFoundError('Config file "' + self.filename + '" is not found.')

    @property
    def data(self) -> dict:
        """
        Return the config from a specific file.
        """
        with open(self.filename, "rb", buffering=1024) as file:
            return json.loads(file.read())

    @data.setter
    def data(self, data) -> None:
        """
        Save the config to a specific file.
        """
        with open(self.filename, "w", buffering=1024) as file:
            file.write(json.dumps(data))


if __name__ == "__main__":
    cm = cl_conf_manager("config.json")
    a=cm.data
    cm.data=a
