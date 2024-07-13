import pytest
from schema import Schema

from user.models import ServiceUser


@pytest.mark.django_db
def test_user_login(api_client):
    """
    유저 로그인 성공 테스트.
    token 값에 대한 검증은 AuthenticationService의 책임.
    로그인 테스트에서는 token이 리턴되는지만 확인하면 됨.
    """

    # given
    ServiceUser.objects.create(email="goodpang@test.com")

    # when
    response = api_client.post("/users/log-in", data={"email": "goodpang@test.com"})

    # then
    assert response.status_code == 200
    assert Schema({"results": {"token": str}}).validate(response.json())
