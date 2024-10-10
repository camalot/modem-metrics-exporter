import os
import typing

import yaml
from config.DataStoreConfiguration import DataStoreConfiguration
from config.LoggingConfiguration import LoggingConfiguration
from config.ModemConfiguration import ModemConfiguration
from config.PresentationConfiguration import PresentationConfiguration
from dotenv import find_dotenv, load_dotenv
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars

# Load configs from env
try:  # Try to load env vars from file, if fails pass
    load_dotenv(find_dotenv())
except:  # noqa: E722
    pass


class Configuration:
    def __init__(self, file_path: typing.Optional[str] = ConfigurationDefaults.CONFIG_FILE_PATH):
        self.reload(file_path)

    def reload(self, file_path: typing.Optional[str] = ConfigurationDefaults.CONFIG_FILE_PATH):
        try:
            file_path = EnvVars.CONFIG_FILE.file(ConfigurationDefaults.CONFIG_FILE_PATH)
        except FileNotFoundError:
            file_path = None

        if not file_path or not os.path.exists(file_path):
            file_path = ConfigurationDefaults.CONFIG_FILE_PATH

        base_config = {}
        # if file_path exists and is not none, load the file
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as file:
                print(f"Loading configuration from {file_path}")
                base_config = yaml.safe_load(file)

        self.logging = LoggingConfiguration(base_config)
        self.datastore = DataStoreConfiguration(base_config)
        self.presentation = PresentationConfiguration(base_config)
        self.modem = ModemConfiguration(base_config)
