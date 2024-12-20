import re

import lib.utils as utils
from lib.probes.Probe import Probe


class BroadbandStatisticsProbe(Probe):
    def __init__(self, modem):
        super().__init__(modem)
        self.name = self.__class__.__name__
        self.logger.debug(f'Initializing {self.name}')
        self.endpoint = '/cgi-bin/broadbandstatistics.ha'
        self.stats_pattern = r'<th[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>'
        self.help_pattern = r'<strong>(?P<property>.*?):</strong>\s*(?P<help>.*?)<br\s*/><br\s*/>'
        self.groups = [
            {
                'name': 'broadband',
                'pattern': r'<div.*?><h2>(?P<section>Primary\s+Broadband)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'ethernet',
                'pattern': r'<div.*?><h2>(?P<section>Ethernet\s+Status)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'ipv6',
                'pattern': r'<div.*?><h2>(?P<section>IPv6)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'ipv6',
                'pattern': r'<div.*?><h2>(?P<section>IPv6\s+Statistics)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'ipv4',
                'pattern': r'<div.*?><h2>(?P<section>IPv4\s+Statistics)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': "gpon",
                'pattern': r'<div.*?><h2>(?P<section>GPON\s+Status)</h2></div>\s*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                # 'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            }
        ]

    def parse(self, response) -> dict:
        result = {}
        for group in self.groups:
            matches = re.finditer(group['pattern'], response, re.IGNORECASE | re.DOTALL)
            for _, match in enumerate(matches):
                original_name = utils.strip_string(match.group('section'))
                section = utils.clean_name_string(group.get('name', 'unknown'))
                stats = match.group('stats')
                if section not in result:
                    result[section] = {}
                stats_result = self.parse_stats(section, stats, self.stats_pattern)
                if stats_result:
                    result.update(stats_result)

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

    def parse_stats(self, section, stats, pattern) -> dict:
        result = {}
        matches = re.finditer(pattern, stats, re.IGNORECASE | re.MULTILINE)
        for _, match in enumerate(matches):
            name = utils.strip_string(match.group('name'))
            key = utils.clean_name_string(name)
            value = match.group('value')
            if section not in result:
                result[section] = {}
            if key not in result[section]:
                result[section][key] = {}
            result[section][key] = {'name': name, 'value': value}
        return result
