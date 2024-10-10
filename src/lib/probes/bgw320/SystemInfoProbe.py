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
        self.help_pattern = r'<strong>(?P<property>.*?):</strong>\s*(?P<help>.*?)<br\s*/><br\s*/>'


    def parse(self, response) -> dict:
        result = {}
        matches = re.finditer(self.pattern, response, re.IGNORECASE | re.MULTILINE)
        for _, match in enumerate(matches):
            name = match.group('name').lower().strip().replace('&nbsp;', '').replace(' ', '')
            value = match.group('value')
            result[name] = value

        # get all help text
        matches = re.finditer(self.help_pattern, response, re.IGNORECASE | re.MULTILINE)
        if 'metadata' not in result:
            result['metadata'] = {}
        if 'help' not in result:
            result['metadata']['help'] = {}
        for _, match in enumerate(matches):
            property = match.group('property')
            help = match.group('help')
            result['metadata']['help'][property.replace(' ', '').lower()] = help

        return result
