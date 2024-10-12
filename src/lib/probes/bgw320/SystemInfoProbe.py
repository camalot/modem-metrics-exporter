import re

from lib.probes.Probe import Probe
import lib.utils as utils


class SystemInfoProbe(Probe):
    def __init__(self, modem):
        super().__init__(modem)

        self.name = self.__class__.__name__
        self.logger.debug(f'Initializing {self.name}')
        self.endpoint = '/cgi-bin/sysinfo.ha'

        self.pattern = r'<th[^>]+>(?P<name>.*?)\s*<\/th>\s+?<td[^>]+>(?P<value>.*?)<\/td>'
        self.help_pattern = r'<strong>(?P<property>.*?):</strong>\s*(?P<help>.*?)<br\s*/><br\s*/>'


    def parse(self, response) -> dict:
        result = {}
        matches = re.finditer(self.pattern, response, re.IGNORECASE | re.MULTILINE)
        for _, match in enumerate(matches):
            name = utils.clean_name_string(match.group('name'))
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
            result['metadata']['help'][utils.clean_name_string(property)] = help

        return result
