"""
유저 관련 예외 처리.
"""


class NotAuthorizedException(Exception):
    message = "Not Authorized"


class UserNotFoundException(Exception):
    message = "User Not Found"


class JWTDecodeException(Exception):
    message = "Invalid Token"


class JWTExpiredException(Exception):
    message = "Expired Token"


class UserPointsNotEnoughException(Exception):
    message = "User Points Not Enough"
