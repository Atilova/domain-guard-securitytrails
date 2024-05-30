from fake_useragent import FakeUserAgent

from domain.ValueObjects.user_agent import UserAgentStr


class UserAgent:
    def random(self) -> UserAgentStr:
        ua = FakeUserAgent(browsers=['edge', 'chrome'])
        return UserAgentStr(ua.random)