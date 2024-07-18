from enum import StrEnum


from django.db import models


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

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
        ]