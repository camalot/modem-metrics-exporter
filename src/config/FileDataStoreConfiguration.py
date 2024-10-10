from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class FileDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.path = EnvVars.FILE_DATASTORE_PATH.string(
            YamlVars.FILE_DATASTORE_PATH.string(base, ConfigurationDefaults.FILE_DATASTORE_PATH)
        )
