import os
import typing

import yaml
from config.DataStoreConfiguration import DataStoreConfiguration
from config.LoggingConfiguration import LoggingConfiguration
from config.ModemsConfiguration import ModemsConfiguration
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
    def __init__(self):
        self.reload()

    def reload(self):
        try:
            config_file = EnvVars.CONFIG_FILE.file(ConfigurationDefaults.CONFIG_FILE_PATH)
        except FileNotFoundError:
            config_file = None

        if not config_file or not os.path.exists(config_file):
            config_file = ConfigurationDefaults.CONFIG_FILE_PATH

        base_config = {}
        # if config_file exists and is not none, load the file
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as file:
                base_config = yaml.safe_load(file)

        self.logging = LoggingConfiguration(base_config)
        self.datastore = DataStoreConfiguration(base_config)
        self.presentation = PresentationConfiguration(base_config)
        self.modems = ModemsConfiguration(base_config)
