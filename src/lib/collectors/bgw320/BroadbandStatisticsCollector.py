
from lib.collectors.Collector import Collector

class BroadbandStatisticsCollector(Collector):
    def __init__(self):
        super().__init__()

    def collect(self):
        print("BroadbandStatisticsCollector Collect")
        pass
