import typing


class ProbeResult:
    def __init__(self, modem: str, probe: str, data: typing.Optional[dict], errors: typing.List[dict]):
        self.probe = probe
        self.modem = modem
        self.data = data
        self.errors = errors

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: typing.Optional[dict]):
        if data is None:
            return None
        return ProbeResult(data['modem'], data['probe'], data['data'], data['errors'])
