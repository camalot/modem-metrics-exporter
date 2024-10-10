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

    MODEM_HOST = "192.168.2.254"
    MODEM_USERNAME = ""
    MODEM_PASSWORD = ""
    MODEM_PORT = 80
    MODEM_SCHEME = "http"
    MODEM_TYPE = "bgw320"

    MONGODB_URL = "mongodb://localhost:27017/admin"
    MONGODB_DB = "modemprobe"
    MONGODB_COLLECTION = "modemprobe"

    PRESENTATION_NAMESPACE = "modemprobe"
    PRESENTATION_PORT = 5000
    PRESENTATION_INTERFACE = "0.0.0.0"

    MQTT_HOST = "localhost"
    MQTT_PORT = 1883

    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = "0"
