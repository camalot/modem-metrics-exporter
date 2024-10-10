class ConfigurationDefaults:
    CONFIG_FILE_PATH = "/config/modemprobe.yaml"

    FILE_DATASTORE_PATH = "/data/cache"

    HTTP_READ_URL = None
    HTTP_WRITE_URL = None
    HTTP_READ_METHOD = "GET"
    HTTP_WRITE_METHOD = "POST"
    HTTP_READ_HEADERS = {}
    HTTP_WRITE_HEADERS = {}
    HTTP_READ_TIMEOUT = 5
    HTTP_WRITE_TIMEOUT = 5
    HTTP_READ_AUTH = None
    HTTP_WRITE_AUTH = None
    HTTP_READ_COOKIES = None
    HTTP_WRITE_COOKIES = None
    HTTP_READ_PARAMS = None
    HTTP_WRITE_PARAMS = None
    HTTP_VERIFY_SSL = True

    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    MONGODB_URL = "mongodb://localhost:27017/admin"
    MONGODB_DB = "netprobe"
    MONGODB_COLLECTION = "netprobe"

    MQTT_HOST = "localhost"
    MQTT_PORT = 1883

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = "0"
