import os
import typing
from enum import Enum


class EnvVars(Enum):
    CONFIG_FILE = "MP_CONFIG_FILE"

    LOG_LEVEL = "MP_LOG_LEVEL"
    LOG_FORMAT = "MP_LOG_FORMAT"
    LOG_DATE_FORMAT = "MP_LOG_DATE_FORMAT"

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
