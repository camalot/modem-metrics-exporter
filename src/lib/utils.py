import re
import typing
from datetime import datetime, timedelta
def is_booleanable(value: str) -> bool:
    if value:
        return value.lower() in ('disabled', 'enabled', 'down', 'up', 'unavailable', 'available', 'off', 'on')
    return False

def to_boolean(value: str) -> bool:
    if value:
        return bool(value.lower() in ('true', '1', 't', 'y', 'yes', 'enabled', 'up', 'available', 'on'))
    return False

def to_int_from_boolean(value: bool) -> int:
    return 1 if value else 0

def datetime_to_epoch(value: typing.Optional[datetime]) -> float:
    if not value:
        print('datetime_to_epoch: value is None')
        return 0.0
    return float((value - datetime(1970, 1, 1)).total_seconds())

def is_timedelta(value: str, fmt: str = "") -> bool:
    if ':' not in value:
        return False

    # years:days:hours:minutes:seconds
    values = value.split(":")

    if len(values) > 4 or len(values) < 1:
        return False

    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if len(values) >= 4:
        days = int(values[0])
        hours = int(values[1])
        minutes = int(values[2])
        seconds = int(values[3])
    if len(values) >= 3:
        hours = int(values[0])
        minutes = int(values[1])
        seconds = int(values[2])
    if len(values) >= 2:
        minutes = int(values[0])
        seconds = int(values[1])
    if len(values) >= 1:
        seconds = int(values[0])
    if len(values) == 0 or len(values) > 4:
        return False
    timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return True

def to_timedelta(value: str, fmt: str = "") -> timedelta:
    # days:hours:minutes:seconds
    values = value.split(":")
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if len(values) == 4:
        days = int(values[0])
        hours = int(values[1])
        minutes = int(values[2])
        seconds = int(values[3])
    if len(values) >= 3:
        hours = int(values[0])
        minutes = int(values[1])
        seconds = int(values[2])
    if len(values) >= 2:
        minutes = int(values[0])
        seconds = int(values[1])
    if len(values) >= 1:
        seconds = int(values[0])
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

def is_datetime(value: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False

def to_datetime(value: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> typing.Optional[datetime]:
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        print(f'to_datetime: value {value} is not a valid datetime')
        return None

def to_epoch(value: str, fmt: str = '%Y-%m-%d %H:%M:%S') -> float:
    dt = to_datetime(value, fmt)
    if dt:
        return datetime_to_epoch(dt)
    return 0.0

def is_string_list(value: str, separator: str = ',') -> bool:
    if not value:
        return False
    try:
        return value.index(separator) > -1
    except ValueError:
        return False

def to_string_list(value: str, separator: str = ',') -> typing.List[str]:
    if not value:
        return []
    return value.split(separator)


def clean_name_string(value: str) -> str:
    return clean_string(value.replace(' ', '').replace('-', '')).lower()

def clean_string(value: str) -> str:
    return strip_html_tags(value.strip().replace('%', '').replace('&nbsp;', '').replace('(mbps)', '').replace('(ssid)', '').replace(' nm', '').replace('(', '').replace(')', ''))

def strip_html_tags(value: str) -> str:
    return re.sub(r'<[^>]*>', '', value)
