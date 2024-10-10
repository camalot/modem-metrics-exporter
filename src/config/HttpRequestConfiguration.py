class HttpRequestConfiguration:
    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', None)
        self.method = kwargs.get('method', 'GET')
        self.headers = kwargs.get('headers', {})
        self.timeout = kwargs.get('timeout', 10)
        self.cookies = kwargs.get('cookies', None)
        self.auth = kwargs.get('auth', None)
        self.params = kwargs.get('params', None)

    def merge(self, config: dict):
        self.__dict__.update(config)
