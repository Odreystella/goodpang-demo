from typing import TypeVar, Generic

from ninja import Schema


T = TypeVar("T")


def response(results: dict | list | Schema) -> dict:
    """
    API 응답 목적으로 사용
    """

    return {"results": results}


def error_response(msg: str) -> dict:
    """
    API 응답 목적으로 사용
    """

    return {"results": {"message": msg}}


class ObjectResponse(Schema, Generic[T]):
    """
    스웨거에서 응답 스키마 확인 목적으로 사용
    """

    results: T


class ErrorResponse(Schema):
    """
    스웨거에서 응답 스키마 확인 목적으로 사용
    """

    message: str


class OkResponse(Schema):
    """
    스웨거에서 응답 스키마 확인 목적으로 사용
    """

    detail: str = "ok"
