from enum import Enum


class DataStoreTypes(Enum):
    FILE = "FILE"
    REDIS = "REDIS"
    MQTT = "MQTT"
    MONGODB = "MONGODB"
    HTTP = "HTTP"
    NONE = "NONE"

    @staticmethod
    def from_str(name: str):
        try:
            return DataStoreTypes[name.upper()]
        except KeyError:
            return DataStoreTypes.NONE

    @staticmethod
    def to_list():
        return [x.name for x in DataStoreTypes]
