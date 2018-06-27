class MutualAPIError(Exception):
    pass


class RequestError(MutualAPIError):
    pass


class InitializationError(MutualAPIError):
    pass
