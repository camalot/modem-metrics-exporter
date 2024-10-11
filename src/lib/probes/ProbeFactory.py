
class ProbeFactory:
    @staticmethod
    def create(modem, type: str):
        try:
            # load the collector class from `lib.probes.{modemType}.{type}`
            # dynamically import the module and class
            probe_module = __import__(f"lib.probes.{modem.type}.{type}", fromlist=[type])
            # create an instance of the collector class
            probe = getattr(probe_module, type)(modem)
            return probe
        except ImportError as ie:
            raise ValueError(f"Could not import probe {type} for modem {modem.type}") from ie
