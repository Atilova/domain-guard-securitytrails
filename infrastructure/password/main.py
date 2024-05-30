import string
from random import choice
from itertools import chain

from typing import Optional

from domain.ValueObjects.password import PasswordStr


alphanumeric = tuple(chain(
    string.ascii_letters,
    string.digits,
))

all_alphanumeric = tuple(chain(
    string.ascii_letters,
    string.digits,
    string.punctuation
))

def _get_length(default: int, specific: int) -> int:
    """_get_length"""

    return specific or default

def _get_random_password(characters: tuple[str, ...], length: int):
    """_get_random_password"""

    return ''.join((
        choice(characters)
        for _ in range(length)
    ))


class PasswordGenerator:
    """PasswordGenerator"""

    def __init__(self, default_length: int = 8):
        self.__length = default_length

    def alphanumeric(self, length: Optional[int] = None) -> PasswordStr:

        password = _get_random_password(alphanumeric, _get_length(
            self.__length,
            length
        ))

        return PasswordStr(password)

    def all_alphanumeric(self, length: Optional[int] = None) -> PasswordStr:
        password = _get_random_password(all_alphanumeric, _get_length(
            self.__length,
            length
        ))

        return PasswordStr(password)