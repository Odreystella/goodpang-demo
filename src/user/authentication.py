import time
from typing import TypedDict, ClassVar

from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer
import jwt

from user.exceptions import (
    NotAuthorizedException,
    UserNotFoundException,
    JWTDecodeException,
    JWTExpiredException,
)
from user.models import ServiceUser


class JWTPayload(TypedDict):
    user_id: int
    exp: int


class AuthenticationService:
    """
    jwt 토큰 생성 및 토큰 검증.
    """

    JWT_SECRET_KEY: ClassVar[str] = settings.SECRET_KEY
    JWT_ALGORITHM: ClassVar[str] = "HS256"

    @staticmethod
    def _unix_timestamp(seconds_in_future: int) -> int:
        return int(time.time()) + seconds_in_future

    def encode_token(self, user_id: int) -> str:
        """
        토큰 생성.
        """
        return jwt.encode(
            {
                "user_id": user_id,
                "exp": self._unix_timestamp(seconds_in_future=24 * 60 * 60),
            },  # 하루 동안 유효한 토큰
            self.JWT_SECRET_KEY,
            algorithm=self.JWT_ALGORITHM,
        )

    def verify_token(self, jwt_token: str) -> int:
        """
        토큰 검증.
        """
        try:
            payload: JWTPayload = jwt.decode(
                jwt_token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM]
            )
            user_id: int = payload["user_id"]
            exp: int = payload["exp"]

        except jwt.exceptions.DecodeError:
            raise JWTDecodeException

        except jwt.exceptions.ExpiredSignatureError:
            raise JWTExpiredException

        except Exception as e:  # noqa
            raise NotAuthorizedException

        if exp < self._unix_timestamp(seconds_in_future=0):
            raise NotAuthorizedException

        return user_id


authentication_service = AuthenticationService()


class BearerAuth(HttpBearer):
    """
    Bearer 토큰이 전달되지 않는 등의 에러는 닌자가 처리해줌.
    """

    def authenticate(self, request, token) -> str:
        """
        토큰을 검증하여 유저 인증하는 API.
        """
        user_id: int = authentication_service.verify_token(jwt_token=token)

        if not (user := ServiceUser.objects.filter(id=user_id).first()):
            raise UserNotFoundException

        request.user = user
        return token


class AuthRequest(HttpRequest):
    user: ServiceUser


bearer_auth = BearerAuth()
