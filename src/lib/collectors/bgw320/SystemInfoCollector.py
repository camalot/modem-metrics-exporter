
from lib.collectors.Collector import Collector

class SystemInfoCollector(Collector):
    def __init__(self):
        super().__init__()

    def collect(self):
        print("SystemInfoCollector Collect")
        pass
