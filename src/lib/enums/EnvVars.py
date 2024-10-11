import os
import typing
from enum import Enum


class EnvVars(Enum):
    CONFIG_FILE = "MP_CONFIG_FILE"

    DATASTORE_PROBE_TYPE = "MP_DATASTORE_PROBE_TYPE"
    DATASTORE_SPEEDTEST_TYPE = "MP_DATASTORE_SPEEDTEST_TYPE"
    DATASTORE_PROBE_TOPIC = "MP_DATASTORE_NETPROBE_TOPIC"
    DATASTORE_SPEEDTEST_TOPIC = "MP_DATASTORE_SPEEDTEST_TOPIC"

    FILE_DATASTORE_PATH = "MP_FILE_DATASTORE_PATH"

    HTTP_READ_URL = "MP_HTTP_READ_URL"
    HTTP_WRITE_URL = "MP_HTTP_WRITE_URL"
    HTTP_READ_METHOD = "MP_HTTP_READ_METHOD"
    HTTP_WRITE_METHOD = "MP_HTTP_WRITE_METHOD"
    HTTP_READ_HEADERS = "MP_HTTP_READ_HEADERS"
    HTTP_WRITE_HEADERS = "MP_HTTP_WRITE_HEADERS"
    HTTP_READ_TIMEOUT = "MP_HTTP_READ_TIMEOUT"
    HTTP_WRITE_TIMEOUT = "MP_HTTP_WRITE_TIMEOUT"
    HTTP_READ_AUTH = "MP_HTTP_READ_AUTH"
    HTTP_WRITE_AUTH = "MP_HTTP_WRITE_AUTH"
    HTTP_READ_COOKIES = "MP_HTTP_READ_COOKIES"
    HTTP_WRITE_COOKIES = "MP_HTTP_WRITE_COOKIES"
    HTTP_READ_PARAMS = "MP_HTTP_READ_PARAMS"
    HTTP_WRITE_PARAMS = "MP_HTTP_WRITE_PARAMS"
    HTTP_VERIFY_SSL = "MP_HTTP_VERIFY_SSL"

    LOG_LEVEL = "MP_LOG_LEVEL"
    LOG_FORMAT = "MP_LOG_FORMAT"
    LOG_DATE_FORMAT = "MP_LOG_DATE_FORMAT"

    MQTT_HOST = "MP_MQTT_HOST"
    MQTT_PORT = "MP_MQTT_PORT"
    MQTT_USERNAME = "MP_MQTT_USERNAME"
    MQTT_PASSWORD = "MP_MQTT_PASSWORD"

    MONGODB_URL = "MP_MONGODB_URL"
    MONGODB_DB = "MP_MONGODB_DB"
    MONGODB_COLLECTION = "MP_MONGODB_COLLECTION"

    PRESENTATION_PORT = "MP_PRESENTATION_PORT"
    PRESENTATION_INTERFACE = "MP_PRESENTATION_INTERFACE"
    PRESENTATION_NAMESPACE = "MP_PRESENTATION_NAMESPACE"

    REDIS_HOST = "MP_REDIS_HOST"
    REDIS_PORT = "MP_REDIS_PORT"
    REDIS_DB = "MP_REDIS_DB"
    REDIS_PASSWORD = "MP_REDIS_PASSWORD"

    def expand(self, default: typing.Any = None) -> str:
        result = EnvVars.unquote(os.getenv(self.value, default))
        return result if result else default

    def boolean(self, default: bool) -> bool:
        return bool(self.expand(str(default)).lower() in ('true', '1', 't', 'y', 'yes'))

    def nullable(self, default: typing.Any = None) -> typing.Optional[str]:
        return self.expand(default) or None

    def string(self, default: str = '') -> str:
        return str(self.expand(default))

    def integer(self, default: int = 0) -> int:
        return int(self.expand(str(default)))

    def float(self, default: float = 0.0) -> float:
        return float(self.expand(str(default)))

    def list(self, separator: str = ',', default: typing.List[str] = []) -> typing.List[str]:
        value = self.expand(separator.join(default))
        if value:
            # split and trim the values
            return [x.strip() for x in self.expand(separator.join(default)).split(separator)]
        return default

    # take key=value pairs separated by a separator and return a dictionary
    def dict(self, separator: str = ";", default: typing.Dict[str, str] = {}) -> typing.Dict[str, str]:
        result = self.nullable_dict(separator, default)
        if result:
            return result
        return {}

    def nullable_dict(
        self, separator: str = ";", default: typing.Optional[typing.Dict[str, str]] = {}
    ) -> typing.Optional[typing.Dict[str, str]]:
        if default:
            # split and trim the values
            return {
                x.split("=")[0].strip(): x.split("=")[1].strip()
                for x in self.expand(separator.join(default)).split(separator)
            }
        return None

    def file(self, default: str = '') -> str:
        fp = self.string(default)
        if not os.path.exists(fp) and default and not os.path.exists(default):
            raise FileNotFoundError(f"File '{fp}' not found")
        return fp

    @staticmethod
    def unquote(value: typing.Optional[str]) -> typing.Any:
        """This function removes quotes from a string if they exist. It is used to clean up environment variables.
        as they can be read with quotes if they are set in a docker-compose file or a .env file."""
        if not value:
            return None

        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value
