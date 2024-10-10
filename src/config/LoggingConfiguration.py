import logging

from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class LoggingConfiguration:
    def __init__(self, base: dict = {}):
        log_level = EnvVars.LOG_LEVEL.string(YamlVars.LOG_LEVEL.string(base, ConfigurationDefaults.LOG_LEVEL)).upper()
        self.level = getattr(logging, log_level, logging.INFO)
        self.format = EnvVars.LOG_FORMAT.string(YamlVars.LOG_FORMAT.string(base, ConfigurationDefaults.LOG_FORMAT))
        self.date_format = EnvVars.LOG_DATE_FORMAT.string(
            YamlVars.LOG_DATE_FORMAT.string(base, ConfigurationDefaults.LOG_DATE_FORMAT)
        )

    def merge(self, config: dict):
        self.__dict__.update(config)
