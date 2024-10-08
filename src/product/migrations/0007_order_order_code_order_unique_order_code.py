# Generated by Django 5.0.1 on 2024-08-24 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0006_order_orderline_order_order_user_id_c70408_idx"),
        ("user", "0004_serviceuser_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_code",
            field=models.CharField(default="", max_length=32),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                fields=("order_code",), name="unique_order_code"
            ),
        ),
    ]
