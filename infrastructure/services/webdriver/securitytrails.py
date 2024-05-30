from seleniumbase import Driver
from seleniumbase.common.exceptions import TextNotVisibleException, NoSuchElementException

from .errors import (
    WebDriverServerError,
    WebDriverCaptchaError,
    WebDriverElementMissingError
)

from domain.ValueObjects.app import Password, SignUpConfirmationLink, ApiKey
from domain.ValueObjects.mail import EmailName, EmailFirstname


PAGES = {
    'sign_up': 'https://securitytrails.com/app/signup',
    'credentials': 'https://securitytrails.com/app/account/credentials',
    'confirm': lambda link: link
}

SELECTORS = {
    'xpath': {
        'api_key_td': ('xpath', '//td[@class="whitespace-nowrap"]')
    },
    'text': {
        'sign_up_opened': ('Sign up - Free', 'h1'),
        'invalid_captcha': ('Invalid recaptcha', 'div'),
        'account_created': ('Congratulations!', 'div'),
        'server_error': ('Something went wrong while connecting to the server', 'div')
    },
    'css': {
        'name_input': '#name',
        'email_input': '#email',
        'password_input': '#password',
        'terms_checkbox': 'label[for="accept-terms-service"]',
        'submit_button': 'button[name="signup-buton"]',
    }
}


class SignupWebDriverService:
    """SignupWebDriverService"""

    def __init__ (self, driver: Driver):
        self.__driver = driver

    def open(self):
        self.__driver.get(PAGES['sign_up'])

        try:
            if self.__driver.assert_text(*SELECTORS['text']['sign_up_opened'], timeout=3):
                return
        except TextNotVisibleException:
            raise WebDriverElementMissingError('Failed to load.')

    def fill_form(self, *, email: EmailName, first_name: EmailFirstname, password: Password):                
        self.__driver.type(SELECTORS['css']['name_input'], first_name.raw())
        self.__driver.type(SELECTORS['css']['email_input'], email.raw())
        self.__driver.type(SELECTORS['css']['password_input'], password.raw())
        self.__driver.click(SELECTORS['css']['terms_checkbox'])

    def submit_form(self):
        self.__driver.click(SELECTORS['css']['submit_button'])

        try:
            self.__driver.assert_text(*SELECTORS['text']['account_created'], timeout=5)
            return
        except TextNotVisibleException:
            pass

        try:
            self.__driver.assert_text(*SELECTORS['text']['invalid_captcha'], timeout=5)
            raise WebDriverCaptchaError('Failed to pass captcha.')
        except TextNotVisibleException:
            pass
        
        try:
            self.__driver.assert_text(*SELECTORS['text']['server_error'], timeout=5)
            raise WebDriverServerError('Failed to register, server error.')
        except TextNotVisibleException:
            pass
        
        raise WebDriverServerError('Registration failed.')

    def confirm_sign_up(self, link: SignUpConfirmationLink):
        self.__driver.open(PAGES['confirm'](link.raw()))

    def get_credentials(self) -> ApiKey:
        self.__driver.open(PAGES['credentials'])

        try:
            td = self.__driver.find_element(*SELECTORS['xpath']['api_key_td'])
        except NoSuchElementException:
            raise WebDriverElementMissingError('ApiKey was not found.')
        
        return ApiKey(td.text)