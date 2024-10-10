

def to_boolean(value: str) -> bool:
    return bool(value.lower() in ('true', '1', 't', 'y', 'yes', 'enabled', 'up', 'available', 'on'))

def to_int_from_boolean(value: bool) -> int:
    return 1 if value else 0
