import json
import re
import requests

from lib.probes.Probe import Probe

class SystemInfoProbe(Probe):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.logger.debug(f'Starting {self.name}')
        self.topic = 'modemprobe/systeminfo'
        self.endpoint = '/cgi-bin/sysinfo.ha'
        self.enabled = True
        self.pattern = r'<th[^>]+>(?P<name>.*?)\s*<\/th>\s+?<td[^>]+>(?P<value>.*?)<\/td>'


    def parse(self, response) -> dict:
        result = {}
        matches = re.finditer(self.pattern, response, re.IGNORECASE | re.MULTILINE)
        for _, match in enumerate(matches):
            name = match.group('name')
            value = match.group('value')
            result[name] = value
        return result
