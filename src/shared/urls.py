from django.contrib import admin
from django.urls import path

from ninja import NinjaAPI

from user.authentication import bearer_auth
from user.exceptions import (
    NotAuthorizedException,
    UserNotFoundException,
    JWTDecodeException,
    JWTExpiredException,
)
from user.urls import router as user_router


base_api = NinjaAPI(title="Goodpang", version="0.0.0")

base_api.add_router("users", user_router)


@base_api.get("")
def health_check_handler(request):
    """
    서버 헬스 체크하는 API.
    """
    return {"ping": "pong"}


@base_api.get("/auth-test", auth=bearer_auth)
def auth_test(request):
    return {
        "token": request.auth,
        "email": request.user.email,
    }


@base_api.exception_handler(NotAuthorizedException)
def not_authorized_exception(request, exc):
    """
    인증 실패한 경우, 에러 응답 만들어줌.
    """
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )


@base_api.exception_handler(UserNotFoundException)
def user_not_found_exception(request, exc):
    """
    유저 존재하지 않는 경우, 에러 응답 만들어줌.
    """
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=404,
    )


@base_api.exception_handler(JWTDecodeException)
def jwt_decode_exception(request, exc):
    """
    jwt 토큰 디코딩 실패하는 경우, 에러 응답 만들어줌.
    """
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )


@base_api.exception_handler(JWTExpiredException)
def jwt_expired_exception(request, exc):
    """
    jwt 토큰 만료한 경우, 에러 응답 만들어줌.
    """
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )


urlpatterns = [
    path("", base_api.urls),
    path("admin/", admin.site.urls),
]
