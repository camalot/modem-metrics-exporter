from config.HttpRequestConfiguration import HttpRequestConfiguration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.EnvVars import EnvVars
from lib.enums.YamlVars import YamlVars


class HttpDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.verify_ssl = EnvVars.HTTP_VERIFY_SSL.boolean(
            YamlVars.HTTP_VERIFY_SSL.boolean(base, ConfigurationDefaults.HTTP_VERIFY_SSL)
        )

        self.read = HttpRequestConfiguration(
            url=(
                EnvVars.HTTP_READ_URL.nullable(
                    YamlVars.HTTP_READ_URL.nullable(base, ConfigurationDefaults.HTTP_READ_URL)
                )
            ),
            method=(
                EnvVars.HTTP_READ_METHOD.string(
                    YamlVars.HTTP_READ_METHOD.string(base, ConfigurationDefaults.HTTP_READ_METHOD)
                )
            ),
            headers=(
                EnvVars.HTTP_READ_HEADERS.nullable_dict(
                    default=YamlVars.HTTP_READ_HEADERS.expand(base, ConfigurationDefaults.HTTP_READ_HEADERS)
                )
            ),
            timeout=(
                EnvVars.HTTP_READ_TIMEOUT.integer(
                    YamlVars.HTTP_READ_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_READ_TIMEOUT)
                )
            ),
            auth=(
                EnvVars.HTTP_READ_AUTH.nullable_dict(
                    default=YamlVars.HTTP_READ_AUTH.expand(base, ConfigurationDefaults.HTTP_READ_AUTH)
                )
            ),
            cookies=(
                EnvVars.HTTP_READ_COOKIES.nullable_dict(
                    default=YamlVars.HTTP_READ_COOKIES.expand(base, ConfigurationDefaults.HTTP_READ_COOKIES)
                )
            ),
            params=(
                EnvVars.HTTP_READ_PARAMS.nullable_dict(
                    default=YamlVars.HTTP_READ_PARAMS.expand(base, ConfigurationDefaults.HTTP_READ_PARAMS)
                )
            ),
        )
        self.write = HttpRequestConfiguration(
            url=(
                EnvVars.HTTP_WRITE_URL.nullable(
                    YamlVars.HTTP_WRITE_URL.nullable(base, ConfigurationDefaults.HTTP_WRITE_URL)
                )
            ),
            method=(
                EnvVars.HTTP_WRITE_METHOD.string(
                    YamlVars.HTTP_WRITE_METHOD.string(base, ConfigurationDefaults.HTTP_WRITE_METHOD)
                )
            ),
            headers=(
                EnvVars.HTTP_WRITE_HEADERS.nullable_dict(
                    default=YamlVars.HTTP_WRITE_HEADERS.expand(base, ConfigurationDefaults.HTTP_WRITE_HEADERS)
                )
            ),
            timeout=(
                EnvVars.HTTP_WRITE_TIMEOUT.integer(
                    YamlVars.HTTP_WRITE_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_WRITE_TIMEOUT)
                )
            ),
            auth=(
                EnvVars.HTTP_WRITE_AUTH.nullable_dict(
                    default=YamlVars.HTTP_WRITE_AUTH.expand(base, ConfigurationDefaults.HTTP_WRITE_AUTH)
                )
            ),
            cookies=(
                EnvVars.HTTP_WRITE_COOKIES.nullable_dict(
                    default=YamlVars.HTTP_WRITE_COOKIES.expand(base, ConfigurationDefaults.HTTP_WRITE_COOKIES)
                )
            ),
            params=(
                EnvVars.HTTP_WRITE_PARAMS.nullable_dict(
                    default=YamlVars.HTTP_WRITE_PARAMS.expand(base, ConfigurationDefaults.HTTP_WRITE_PARAMS)
                )
            ),
        )

    def merge(self, config: dict):
        self.__dict__.update(config)
