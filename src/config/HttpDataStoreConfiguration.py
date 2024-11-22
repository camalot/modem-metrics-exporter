from config.HttpRequestConfiguration import HttpRequestConfiguration
from lib.enums.ConfigurationDefaults import ConfigurationDefaults
from lib.enums.YamlVars import YamlVars


class HttpDataStoreConfiguration:
    def __init__(self, base: dict = {}):
        self.verify_ssl = YamlVars.HTTP_VERIFY_SSL.boolean(base, ConfigurationDefaults.HTTP_VERIFY_SSL)
        self.read = HttpRequestConfiguration(
            url=YamlVars.HTTP_READ_URL.nullable(base, ConfigurationDefaults.HTTP_READ_URL),
            method=YamlVars.HTTP_READ_METHOD.string(base, ConfigurationDefaults.HTTP_READ_METHOD),
            headers=YamlVars.HTTP_READ_HEADERS.expand(base, ConfigurationDefaults.HTTP_READ_HEADERS),
            timeout=YamlVars.HTTP_READ_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_READ_TIMEOUT),
            auth=YamlVars.HTTP_READ_AUTH.expand(base, ConfigurationDefaults.HTTP_READ_AUTH),
            cookies=YamlVars.HTTP_READ_COOKIES.expand(base, ConfigurationDefaults.HTTP_READ_COOKIES),
            params=YamlVars.HTTP_READ_PARAMS.expand(base, ConfigurationDefaults.HTTP_READ_PARAMS),
        )
        self.write = HttpRequestConfiguration(
            url=YamlVars.HTTP_WRITE_URL.nullable(base, ConfigurationDefaults.HTTP_WRITE_URL),
            method=YamlVars.HTTP_WRITE_METHOD.string(base, ConfigurationDefaults.HTTP_WRITE_METHOD),
            headers=YamlVars.HTTP_WRITE_HEADERS.expand(base, ConfigurationDefaults.HTTP_WRITE_HEADERS),
            timeout=YamlVars.HTTP_WRITE_TIMEOUT.integer(base, ConfigurationDefaults.HTTP_WRITE_TIMEOUT),
            auth=YamlVars.HTTP_WRITE_AUTH.expand(base, ConfigurationDefaults.HTTP_WRITE_AUTH),
            cookies=YamlVars.HTTP_WRITE_COOKIES.expand(base, ConfigurationDefaults.HTTP_WRITE_COOKIES),
            params=YamlVars.HTTP_WRITE_PARAMS.expand(base, ConfigurationDefaults.HTTP_WRITE_PARAMS),
        )

    def merge(self, config: dict):
        self.__dict__.update(config)
