import pytest
from schema import Schema

from product.models import Product, ProductStatus, OrderLine, Order, OrderStatus
from user.models import ServiceUser
from user.authentication import authentication_service


@pytest.mark.django_db  # 테스트 함수에서 DB 사용이 필요
def test_get_product_list(api_client):
    """
    노출된 상품 목록 가져오기 성공 테스트.
    """

    # given
    Product.objects.create(name="청바지", price=1, status="active")

    # when
    response = api_client.get("/products")

    # then
    assert response.status_code == 200
    assert len(response.json()["results"]["products"]) == 30
    # assert Schema(
    #     {"results": {"products": [{"id": int, "name": "청바지", "price": 1}]}}
    # ).validate(response.json())


@pytest.mark.django_db
def test_order_products(api_client):
    """
    주문 생성 API 성공 테스트.
    """
    # given
    user = ServiceUser.objects.create(email="goodpang@example.com")
    token = authentication_service.encode_token(user_id=user.id)

    p1 = Product.objects.create(name="청바지", price=1000, status=ProductStatus.ACTIVE)
    p2 = Product.objects.create(name="티셔츠", price=500, status=ProductStatus.ACTIVE)

    # when
    response = api_client.post(
        "/products/orders",
        data={
            "order_lines": [
                {"product_id": p1.id, "quantity": 2},
                {"product_id": p2.id, "quantity": 3},
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # then
    assert response.status_code == 201
    assert Schema(
        {
            "results": {
                "id": int,
                "total_price": int((p1.price * 2 * 0.9) + (p2.price * 3 * 0.9)),
            }
        }
    ).validate(response.json())

    order_id = response.json()["results"]["id"]
    assert OrderLine.objects.filter(order_id=order_id).count() == 2


@pytest.mark.django_db
def test_confirm_order(api_client):
    """
    주문에 대한 결제 확인 API 성공 테스트
    """
    # given
    user = ServiceUser.objects.create(email="goodpang@example.com", points=1000)
    token = authentication_service.encode_token(user_id=user.id)

    order = Order.objects.create(
        user=user, total_price=1000, status=OrderStatus.PENDING
    )

    # when
    response = api_client.post(
        f"/products/orders/{order.id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
    )

    # then
    assert response.status_code == 200
    assert Schema({"results": {"detail": "ok"}}).validate(response.json())

    assert Order.objects.get(id=order.id).status == OrderStatus.PAID
    assert ServiceUser.objects.get(id=user.id).order_count == 1
    assert ServiceUser.objects.get(id=user.id).points == 0
