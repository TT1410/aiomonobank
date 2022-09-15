"""
 - MonobankError
    - ValidationError
    - BadRequest
        - InvalidAccount
        - PeriodError
    - Unauthorized
        - InvalidToken
    - RetryAfter
    - WebhookUrlError
    - NetworkError
"""


class MonobankError(Exception):
    def __init__(self, message=None):
        super(MonobankError, self).__init__(message)


class _MatchErrorMixin:
    match = ''
    text = None

    __subclasses = []

    def __init_subclass__(cls, **kwargs):
        super(_MatchErrorMixin, cls).__init_subclass__(**kwargs)
        # cls.match = cls.match.lower() if cls.match else ''
        if not hasattr(cls, f"_{cls.__name__}__group"):
            cls.__subclasses.append(cls)

    @classmethod
    def check(cls, message) -> bool:
        """
        Compare pattern with message

        :param message: always must be in lowercase
        :return: bool
        """
        return cls.match.lower() in message

    @classmethod
    def detect(cls, description):
        description = description.lower()
        for err in cls.__subclasses:
            if err is cls:
                continue
            if err.check(description):
                raise err(cls.text or description)
        raise cls(description)


class ValidationError(MonobankError):
    pass


class BadRequest(MonobankError, _MatchErrorMixin):
    __group = True


class InvalidAccount(BadRequest):
    match = "invalid account"
    text = "Invalid account"


class PeriodError(BadRequest):
    match = "Period must be no more than 31 days"


class Unauthorized(MonobankError, _MatchErrorMixin):
    __group = True


class InvalidToken(Unauthorized):
    match = 'Unknown \'X-Token\''
    text = 'Invalid token or it has been revoked. ' \
           'Get a new token on the page https://api.monobank.ua'


class RetryAfter(MonobankError):
    def __init__(self, retry_after=60):
        super(RetryAfter, self).__init__(f"Flood control exceeded. Retry in {retry_after} seconds.")
        self.timeout = retry_after


class WebhookUrlError(MonobankError):
    pass


class NetworkError(MonobankError):
    pass
