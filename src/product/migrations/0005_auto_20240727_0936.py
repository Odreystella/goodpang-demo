# Generated by Django 5.0.1 on 2024-07-27 09:36

import random

from django.db import migrations


def create_products(apps, schema_editor):
    """
    product에 10만개 상품 데이터 대량 생성하는 함수.
    """
    Product = apps.get_model("product", "Product")

    adv = ["진짜", "정말", "매우"]
    adj = ["예쁜", "멋있는", "좋은"]
    products = ["청바지", "티셔츠", "자켓"]

    for _ in range(50):
        to_create = []
        for _ in range(2000):
            name = (
                f"{random.choice(adv)} {random.choice(adj)} {random.choice(products)}"
            )
            to_create.append(Product(name=name, price=100, status="active"))

        Product.objects.bulk_create(to_create)


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0004_product_product_name_gin_index"),
    ]

    operations = [
        migrations.RunPython(create_products, reverse_code=migrations.RunPython.noop),
    ]
