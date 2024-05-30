from typing import Any


def dictget(d: dict, /, *keys: tuple[str], default=None) -> list[Any]:
    """dictget"""
    
    return [d.get(key, default) for key in keys]