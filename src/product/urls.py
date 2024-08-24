from typing import List, Dict

from django.http import HttpRequest
from django.db import transaction
from django.db.models import F
from ninja import Router

from product.models import (
    Product,
    ProductStatus,
    Category,
    Order,
    OrderLine,
    OrderStatus,
)
from product.request import OrderRequestBody
from product.response import (
    ProductListResponse,
    CategoryListResponse,
    OrderDetailResponse,
)
from product.exceptions import (
    OrderInvalidProductException,
    OrderNotFoundException,
    OrderAlreadyPaidException,
)
from shared.response import (
    ObjectResponse,
    response,
    error_response,
    ErrorResponse,
    OkResponse,
)
from user.authentication import bearer_auth, AuthRequest
from user.exceptions import UserPointsNotEnoughException, UserVersionConflictException
from user.models import ServiceUser


router = Router(tags=["Products"])


@router.get(
    "",
    response={
        200: ObjectResponse[ProductListResponse],
    },
)
def product_list_handler(
    request: HttpRequest, category_id: int | None = None, query: str | None = None
):
    """
    쿼리 파라미터인 category_id, query에 따라 상품 목록 조회 API
    """
    if query:
        products = Product.objects.filter(
            name__contains=query, status=ProductStatus.ACTIVE
        )
    elif category_id:
        category: Category | None = Category.objects.filter(id=category_id).first()
        if not category:
            products = []
        else:
            # category_id: 1 -> [의류.id] + [상의.id, 하의.id]
            # category_id: 2 -> [상의.id] + []
            category_ids: List[int] = [category.id] + list(
                category.children.values_list("id", flat=True)
            )
            products = Product.objects.filter(
                category_id__in=category_ids, status=ProductStatus.ACTIVE
            ).values("id", "name", "price")
    else:
        products = Product.objects.filter(status=ProductStatus.ACTIVE).values(
            "id", "name", "price"
        )

    return 200, response(ProductListResponse(products=products[:30]))


@router.get(
    "/categories",
    response={
        200: ObjectResponse[CategoryListResponse],
    },
)
def categories_list_handler(request: HttpRequest):
    """
    카테고리 목록 조회 API
    N+1쿼리 방지
    """
    return 200, response(
        CategoryListResponse.build(
            categories=Category.objects.filter(parent=None).prefetch_related("children")
        )
    )


@router.post(
    "/orders",
    response={
        201: ObjectResponse[OrderDetailResponse],
        400: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def order_products_handler(request: AuthRequest, body: OrderRequestBody):
    """
    주문 생성 API
    Order, OrderLine 트랜잭션으로 처리
    """
    product_id_to_quantity: Dict[int, int] = body.product_id_to_quantity

    products: List[Product] = list(
        Product.objects.filter(
            id__in=product_id_to_quantity, status=ProductStatus.ACTIVE
        )
    )
    if len(products) != len(product_id_to_quantity):
        return 400, error_response(msg=OrderInvalidProductException.message)

    with transaction.atomic():
        total_price: int = 0
        order = Order.objects.create(user=request.user)

        order_lines_to_create: List[OrderLine] = []
        for product in products:
            price: int = product.price
            discount_ratio: float = 0.9
            quantity: int = product_id_to_quantity[product.id]

            order_lines_to_create.append(
                OrderLine(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    discount_ratio=discount_ratio,
                )
            )

            total_price += price * quantity * discount_ratio

        order.total_price = int(total_price)
        order.save()
        OrderLine.objects.bulk_create(objs=order_lines_to_create)

    return 201, response({"id": order.id, "total_price": order.total_price})


@router.post(
    "/orders/{order_id}/confirm",
    response={
        200: ObjectResponse[OkResponse],
        400: ObjectResponse[ErrorResponse],
        404: ObjectResponse[ErrorResponse],
        409: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def confirm_order_payment_handler(request: AuthRequest, order_id: int):
    """
    주문에 대해 결제의 승인여부를 확인하고, 완료 시 상태값을 PENDING -> PAID 변경하는 API
    """
    if not (
        order := Order.objects.filter(id=order_id, user=request.user).first()
    ):  # := 할당 표현식, python 3.8이상부터
        return 404, error_response(msg=OrderNotFoundException.message)

    with transaction.atomic():
        success: int = Order.objects.filter(
            id=order_id, status=OrderStatus.PENDING
        ).update(status=OrderStatus.PAID)  # Compare-and-Swap, 업데이트 한 rows 수 반환
        if not success:
            return 400, error_response(msg=OrderAlreadyPaidException.message)

        user = ServiceUser.objects.get(id=request.user.id)
        if user.points < order.total_price:
            return 409, error_response(msg=UserPointsNotEnoughException.message)

        success: int = ServiceUser.objects.filter(
            id=request.user.id,
            version=user.version,
        ).update(
            order_count=F("order_count") + 1,
            points=F("points") - order.total_price,
            version=user.version + 1,
        )  # version 필드를 사용한 낙관적 락 방법

        if not success:
            # Order의 상태 변경은 성공적인데, User version 변경에서 충돌이 난 경우 재시도 등 처리가 필요함
            return 409, error_response(msg=UserVersionConflictException.message)

    return 200, response(OkResponse())
