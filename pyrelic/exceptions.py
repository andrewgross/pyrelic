class NewRelicApiException(Exception):
    def __init__(self, message):
        super(NewRelicApiException, self).__init__()
        print message


class NewRelicInvalidApiKeyException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidApiKeyException, self).__init__(message)
        pass


class NewRelicCredentialException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicCredentialException, self).__init__(message)
        pass


class NewRelicInvalidParameterException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidParameterException, self).__init__(message)
        pass


class NewRelicUnknownApplicationException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicUnknownApplicationException, self).__init__(message)
        pass


class NewRelicApiRateLimitException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicApiRateLimitException, self).__init__(message)
        self.timeout = message
