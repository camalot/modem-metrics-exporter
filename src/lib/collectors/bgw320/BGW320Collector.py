from lib.collectors.Collector import Collector

class BGW320Collector(Collector):
    def __init__(self, modem):
        super().__init__(modem)
        self.subspace = ''

    def get_help(self, key: str, metadata: dict) -> str:
        if key in metadata['help']:
            return metadata['help'][key]
        return ''
