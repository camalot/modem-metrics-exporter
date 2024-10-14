import re

from lib.probes.Probe import Probe
import lib.utils as utils


class HomeNetworkStatsProbe(Probe):
    def __init__(self, modem):
        super().__init__(modem)
        self.name = self.__class__.__name__
        self.logger.debug(f'Initializing {self.name}')
        self.endpoint = '/cgi-bin/lanstatistics.ha'

        self.help_pattern = r'<strong>(?P<property>.*?):</strong>\s*(?P<help>.*?)<br\s*/><br\s*/>'

        self.groups = [
            {
                'name': 'network status',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<div.*?>\s*<h\d>(?P<section>Home\sNetwork\sStatus)</h\d>\s*</div>\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'interfaces',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<div.*?>\s*<h\d>(?P<section>Interfaces)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<td[^>]*>(?P<name>.*?)\s*<\/td>\s*?<td[^>]*>\s*?(?P<status>.*?)\s*?<\/td>\s*<td[^>]*>\s*?(?P<active>.*?)\s*?<\/td>\s*<td[^>]*>\s*?(?P<inactive>.*?)\s*?<\/td>',
            },
            {
                'name': 'ipv6',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<div.*?>\s*<h\d>(?P<section>IPv6)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'ipv4',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<div.*?>\s*<h\d>(?P<section>IPv4 Statistics)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<th[^>]*>(?P<name>.*?)\s*<\/th>\s*?<td[^>]*>\s*?(?P<value>.*?)\s*?<\/td>',
            },
            {
                'name': 'wifi status',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<h\d>(?P<section>Wi\-Fi\sStatus)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<td[^>]*>(?!&nbsp;)(?P<name>.*?)\s*<\/td>\s*?\s*<td[^>]*>\s*?(?P<ghz24>.*?)\s*?<\/td>\s*(?:<td[^>]*>\s*?(?P<ghz5>.*?)\s*?<\/td>\s*</tr>)?',
            },
            {
                'name': 'wifi statistics',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<h\d>(?P<section>Wi\-Fi\sNetwork\sStatistics)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<td[^>]*>(?!&nbsp;)(?P<name>.*?)\s*<\/td>\s*?\s*<td[^>]*>\s*?(?P<ghz24>.*?)\s*?<\/td>\s*(?:<td[^>]*>\s*?(?P<ghz5>.*?)\s*?<\/td>\s*</tr>)?',
            },
            {
                'name': 'lan',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<h\d>(?P<section>LAN\sEthernet\sStatistics)</h\d>\s*\s*.*?<table[^>]*>(?P<stats>.*?)</table>',
                'stats': r'<td[^>]*>(?!&nbsp;)(?P<name>.*?)\s*<\/td>\s*?\s*<td[^>]*>\s*?(?P<port1>.*?)\s*?<\/td>\s*<td[^>]*>\s*?(?P<port2>.*?)\s*?<\/td>\s*<td[^>]*>\s*?(?P<port3>.*?)\s*?<\/td>\s*<td[^>]*>\s*?(?P<port4>.*?)\s*?<\/td>\s*</tr>',
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
                if 'value' in match.groupdict():
                    result[section]['value'] = match.group('value')
                    if 'name' not in result[section]:
                        result[section]['name'] = original_name
                stats_result = self.parse_stats(section, stats, group['stats'], options=group['options'])
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

    def parse_stats(self, section, stats, pattern, **kwargs) -> dict:
        result = {}
        matches = re.finditer(pattern, stats, kwargs['options'])
        for _, match in enumerate(matches):
            original_name = utils.strip_string(match.group('name'))
            name = utils.clean_name_string(original_name)

            if section not in result:
                result[section] = {}
            if name not in result[section]:
                result[section][name] = {}

            match_group = match.groupdict()
            group_keys = match_group.keys()
            if len(group_keys) == 2 and 'name' in group_keys and 'value' in group_keys:
                result[section][name]['value'] = utils.clean_string(match.group('value'))
                result[section][name]['name'] = original_name
            else:
                for x in match.groupdict().keys():
                    mval = match.group(x)
                    if mval:
                        result[section][name][x] = utils.clean_string(match.group(x))
                    else:
                        result[section][name][x] = None
        return result
