from config.ModemConfiguration import ModemConfiguration

class ModemsConfiguration(list):
    def __init__(self, base_config: dict):
        for modem in base_config.get('modems', []):
            self.append(ModemConfiguration(modem))
