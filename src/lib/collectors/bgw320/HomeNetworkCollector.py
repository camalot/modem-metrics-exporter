
from lib.collectors.Collector import Collector

class HomeNetworkCollector(Collector):
    def __init__(self):
        super().__init__()

    def collect(self):
        print("HomeNetworkCollector Collect")
        pass
