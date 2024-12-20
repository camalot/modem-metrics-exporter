import re

import lib.utils as utils
from lib.probes.Probe import Probe


class FiberStatusProbe(Probe):
    def __init__(self, modem):
        super().__init__(modem)
        self.name = self.__class__.__name__
        self.logger.debug(f'Initializing {self.name}')

        self.endpoint = '/cgi-bin/fiberstat.ha'
        self.help_pattern = r'<strong>(?P<property>.*?):</strong>\s*(?P<help>.*?)<br\s*/><br\s*/>'

        self.groups = [
            {
                'name': 'fiber',
                'options': re.IGNORECASE | re.DOTALL | re.MULTILINE,
                'pattern': r'<h1>\s*(?P<section>Fiber\s+Status)\s*</h1>\s*?.*?<div>\s*(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<th[^>]*>(?P<name>.*?)\s*?<\/th>\s*<td[^>]*>(?P<value>.*?)<\/td>',
            },
            {
                'name': 'temperature',
                'options': re.IGNORECASE | re.MULTILINE,
                'pattern': r'<h1>(?P<section>Temperature)(:?&nbsp;){2}Currently\s*(?P<value>.*?)\s*</h1>\s*?<table.*?>(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<td[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/td>\s*?<td[^>]*>\s*?(?P<low>\d{1,})\s*\(Threshold\s*(?P<lowT>\-?\d{1,}\.\d{1,})\)<\/td>\s*<td[^>]*>\s*?(?P<high>\d{1,})\s*\(Threshold\s*(?P<highT>\-?\d{1,}\.\d{1,})\)<\/td>\s*',
            },
            {
                'name': 'vcc',
                'options': re.IGNORECASE | re.MULTILINE,
                'pattern': r'<h1>(?P<section>Vcc)(:?&nbsp;){2}Currently\s*(?P<value>.*?)\s*</h1>\s*?<table.*?>(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<td[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/td>\s*?<td[^>]*>\s*?(?P<low>\d{1,})\s*\(Threshold\s*(?P<lowT>\-?\d{1,}\.\d{1,})\)<\/td>\s*<td[^>]*>\s*?(?P<high>\d{1,})\s*\(Threshold\s*(?P<highT>\-?\d{1,}\.\d{1,})\)<\/td>\s*',
            },
            {
                'name': 'txbias',
                'options': re.IGNORECASE | re.MULTILINE,
                'pattern': r'<h1>(?P<section>Tx Bias)(:?&nbsp;){2}Currently\s*(?P<value>.*?)\s*</h1>\s*?<table.*?>(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<td[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/td>\s*?<td[^>]*>\s*?(?P<low>\d{1,})\s*\(Threshold\s*(?P<lowT>\-?\d{1,}\.\d{1,})\)<\/td>\s*<td[^>]*>\s*?(?P<high>\d{1,})\s*\(Threshold\s*(?P<highT>\-?\d{1,}\.\d{1,})\)<\/td>\s*',
            },
            {
                'name': 'txpower',
                'options': re.IGNORECASE | re.MULTILINE,
                'pattern': r'<h1>(?P<section>Tx Power)(:?&nbsp;){2}Currently\s*(?P<value>.*?)\s*</h1>\s*?<table.*?>(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<td[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/td>\s*?<td[^>]*>\s*?(?P<low>\d{1,})\s*\(Threshold\s*(?P<lowT>\-?\d{1,}\.\d{1,})\)<\/td>\s*<td[^>]*>\s*?(?P<high>\d{1,})\s*\(Threshold\s*(?P<highT>\-?\d{1,}\.\d{1,})\)<\/td>\s*',
            },
            {
                'name': 'rxpower',
                'options': re.IGNORECASE | re.MULTILINE,
                'pattern': r'<h1>(?P<section>Rx Power)(:?&nbsp;){2}Currently\s*(?P<value>.*?)\s*</h1>\s*?<table.*?>(?P<stats>.*?)</table>\s*</div>',
                'stats': r'<td[^>]*>(?P<name>.*?)(?:&nbsp;)*?\s*<\/td>\s*?<td[^>]*>\s*?(?P<low>\d{1,})\s*\(Threshold\s*(?P<lowT>\-?\d{1,}\.\d{1,})\)<\/td>\s*<td[^>]*>\s*?(?P<high>\d{1,})\s*\(Threshold\s*(?P<highT>\-?\d{1,}\.\d{1,})\)<\/td>\s*',
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
                stats_results = self.parse_stats(section, stats, group['stats'], options=group['options'])
                if stats_results:
                    result.update(stats_results)
                if 'value' in match.groupdict():
                    result[section]['value'] = float(match.group('value') or '0')
                    if 'name' not in result[section]:
                        result[section]['name'] = original_name
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
                    result[section][name][x] = utils.clean_string(match.group(x))
        return result
