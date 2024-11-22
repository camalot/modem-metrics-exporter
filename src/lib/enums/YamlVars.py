import typing
from enum import Enum

import yaql


class YamlVars(Enum):
    DATASTORE_PROBE_TYPE = "$.datastore.probe.type"
    DATASTORE_SPEEDTEST_TYPE = "$.datastore.speedtest.type"
    DATASTORE_PROBE_TOPIC = "$.datastore.probe.topic"
    DATASTORE_SPEEDTEST_TOPIC = "$.datastore.speedtest.topic"

    FILE_DATASTORE_PATH = "$.datastore.file.path"

    HTTP_VERIFY_SSL = "$.datastore.http.verify_ssl"
    HTTP_READ_URL = "$.datastore.http.read.url"
    HTTP_READ_METHOD = "$.datastore.http.read.method"
    HTTP_READ_HEADERS = "$.datastore.http.read.headers"
    HTTP_READ_TIMEOUT = "$.datastore.http.read.timeout"
    HTTP_READ_AUTH = "$.datastore.http.read.auth"
    HTTP_READ_COOKIES = "$.datastore.http.read.cookies"
    HTTP_READ_PARAMS = "$.datastore.http.read.params"
    HTTP_WRITE_URL = "$.datastore.http.write.url"
    HTTP_WRITE_METHOD = "$.datastore.http.write.method"
    HTTP_WRITE_HEADERS = "$.datastore.http.write.headers"
    HTTP_WRITE_TIMEOUT = "$.datastore.http.write.timeout"
    HTTP_WRITE_AUTH = "$.datastore.http.write.auth"
    HTTP_WRITE_COOKIES = "$.datastore.http.write.cookies"
    HTTP_WRITE_PARAMS = "$.datastore.http.write.params"

    LOG_LEVEL = "$.logging.level"
    LOG_FORMAT = "$.logging.format"
    LOG_DATE_FORMAT = "$.logging.date_format"

    MODEMS = "$.modems"
    # These are called from within the modem object. that is why they are "top level"
    MODEM_NAME = "$.name"
    MODEM_HOST = "$.host"
    MODEM_ENABLED = "$.enabled"
    MODEM_USERNAME = "$.username"
    MODEM_PASSWORD = "$.password"
    MODEM_PORT = "$.port"
    MODEM_SCHEME = "$.scheme"
    MODEM_TYPE = "$.type"
    MODEM_COLLECTORS = "$.collectors"
    MODEM_PROBES = "$.probes"

    MONGODB_URL = "$.datastore.mongodb.url"
    MONGODB_DB = "$.datastore.mongodb.db"
    MONGODB_COLLECTION = "$.datastore.mongodb.collection"

    MQTT_HOST = "$.datastore.mqtt.host"
    MQTT_PORT = "$.datastore.mqtt.port"
    MQTT_USERNAME = "$.datastore.mqtt.username"
    MQTT_PASSWORD = "$.datastore.mqtt.password"

    PRESENTATION_PORT = "$.presentation.port"
    PRESENTATION_INTERFACE = "$.presentation.interface"
    PRESENTATION_NAMESPACE = "$.presentation.namespace"

    REDIS_HOST = "$.datastore.redis.host"
    REDIS_PORT = "$.datastore.redis.port"
    REDIS_DB = "$.datastore.redis.db"
    REDIS_PASSWORD = "$.datastore.redis.password"

    __engine__ = yaql.factory.YaqlFactory().create()

    def expand(self, data: dict, default: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        # return default
        try:
            # from yaml use the value of the key to query to expand the data value
            expression = YamlVars.__engine__(self.value)
            result = expression.evaluate(data=data)  # type: ignore
            if result is None:
                return default
            return result
        except KeyError:
            return default

    def nullable(self, data: dict, default: typing.Optional[typing.Any]) -> typing.Optional[typing.Any]:
        return self.expand(data, default) or None

    def string(self, data: dict, default: str) -> str:
        return str(self.expand(data, default))

    def list(self, data: dict, default: typing.List[str]) -> typing.List[str]:
        result = self.expand(data, None) or default
        if result is None:
            return default
        return list(result)

    def boolean(self, data: dict, default: bool) -> bool:
        return bool(self.string(data, str(default)).lower() in ('true', '1', 't', 'y', 'yes', "on", "enabled"))

    def float(self, data: dict, default: float) -> float:
        return float(self.string(data, str(default)))

    def integer(self, data: dict, default: int) -> int:
        return int(self.string(data, str(default)))
