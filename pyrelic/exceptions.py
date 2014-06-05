class NewRelicApiException(Exception):
    def __init__(self, message):
        super(NewRelicApiException, self).__init__()


class NewRelicInvalidApiKeyException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidApiKeyException, self).__init__(message)


class NewRelicCredentialException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicCredentialException, self).__init__(message)


class NewRelicInvalidParameterException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidParameterException, self).__init__(message)


class NewRelicUnknownApplicationException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicUnknownApplicationException, self).__init__(message)


class NewRelicApiRateLimitException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicApiRateLimitException, self).__init__(message)
        self.timeout = message
