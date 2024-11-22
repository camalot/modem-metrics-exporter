class CollectorFactory:
    @staticmethod
    def create(modem, collectorType: str):
        try:
            # load the collector class from `lib.collectors.{modemType}.{collectorType}`
            # dynamically import the module and class
            collector_module = __import__(f"lib.collectors.{modem.type}.{collectorType}", fromlist=[collectorType])
            # create an instance of the collector class
            collector = getattr(collector_module, collectorType)(modem)
            return collector
        except ImportError as ie:
            raise ValueError(f"Could not import collector {collectorType} for modem {modem.type}") from ie
