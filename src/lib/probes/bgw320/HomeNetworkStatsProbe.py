import json
import re
import requests

from lib.probes.Probe import Probe


class HomeNetworkStatsProbe(Probe):
    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.logger.debug(f'Starting {self.name}')
        self.endpoint = '/cgi-bin/lanstatistics.ha'
        self.topic = 'modemprobe/lanstats'
        self.enabled = True
        self.interval = 60
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
                section = group.get('name', 'unknown').lower().strip().replace('&nbsp;', '').replace(' ', '')
                stats = match.group('stats')
                if section not in result:
                    result[section] = {}
                if 'value' in match.groupdict():
                    result[section]['value'] = match.group('value')
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
            result['metadata']['help'][property.replace(' ', '').lower()] = help

        return result

    def parse_stats(self, section, stats, pattern, **kwargs) -> dict:
        result = {}
        matches = re.finditer(pattern, stats, kwargs['options'])
        for _, match in enumerate(matches):
            name = match.group('name').lower().strip().replace('&nbsp;', '').replace(' ', '')

            if section not in result:
                result[section] = {}
            if name not in result[section]:
                result[section][name] = {}

            match_group = match.groupdict()
            group_keys = match_group.keys()
            if len(group_keys) == 2 and 'name' in group_keys and 'value' in group_keys:
                result[section][name] = match.group('value').strip().replace('&nbsp;', '')
            else:
                for x in match.groupdict().keys():
                    mval = match.group(x)
                    if mval:
                        result[section][name][x] = match.group(x).strip().replace('&nbsp;', '')
                    else:
                        result[section][name][x] = None
        return result
