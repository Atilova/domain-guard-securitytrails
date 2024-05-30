from typing import Protocol

from domain.ValueObjects.app import ApiKey, Password, SignUpConfirmationLink
from domain.ValueObjects.mail import EmailName, EmailFirstname


class ISignUpWebDriverService(Protocol):
    """ISignUpWebDriverService"""

    def open():
        pass

    def fill_form(self, *, email: EmailName, first_name: EmailFirstname, password: Password):
        pass

    def submit_form(self):
        pass

    def confirm_sign_up(self, link: SignUpConfirmationLink):
        pass

    def get_credentials(self) -> ApiKey:
        pass
