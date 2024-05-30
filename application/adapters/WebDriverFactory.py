from seleniumbase import SB

from typing import Callable

from .ISignUpWebDriverService import ISignUpWebDriverService


WebDriverFactory = Callable[[SB], ISignUpWebDriverService]