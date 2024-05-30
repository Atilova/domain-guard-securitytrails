from typing import Any, Callable


def notnone_init(value: Any, initializer: Callable):
    """notnone_init"""

    return value is not None and initializer(value) or value