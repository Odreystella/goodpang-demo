from django.http import HttpRequest
from ninja import Router

from product.models import Product, ProductStatus
from product.response import ProductListResponse
from shared.response import ObjectResponse, response


router = Router(tags=["Products"])


@router.get(
    "",
    response={
        200: ObjectResponse[ProductListResponse],
    },
)
def product_list_handler(request: HttpRequest):
    return 200, response(
        ProductListResponse(
            products=Product.objects.filter(status=ProductStatus.ACTIVE).values(
                "id", "name", "price"
            )
        )
    )
