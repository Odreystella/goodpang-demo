from django.http import HttpRequest
from ninja import Router

from product.models import Product, ProductStatus, Category
from product.response import ProductListResponse, CategoryListResponse
from shared.response import ObjectResponse, response


router = Router(tags=["Products"])


@router.get(
    "",
    response={
        200: ObjectResponse[ProductListResponse],
    },
)
def product_list_handler(request: HttpRequest):
    """
    싱품 목록 조회 API
    """
    return 200, response(
        ProductListResponse(
            products=Product.objects.filter(status=ProductStatus.ACTIVE).values(
                "id", "name", "price"
            )
        )
    )


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
