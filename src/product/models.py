from enum import StrEnum

from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class ProductStatus(StrEnum):
    """
    status 필드를 Enum 타입으로 만들기.
    django의 choices 필드를 사용하는 방법도 있음.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=8)  # active | inactive | paused
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=128, blank=True)  # 영문 데이터
    search_vector = SearchVectorField(null=True)  # 형태소 분석 결과를 저장

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
            GinIndex(
                fields=["search_vector"]
            ),  # search_vector를 기준으로 역인덱스 생성
            GinIndex(
                name="product_name_gin_index",
                fields=["name"],
                opclasses=["gin_bigm_ops"],
            ),
        ]


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="children"
    )

    class Meta:
        app_label = "product"
        db_table = "category"
