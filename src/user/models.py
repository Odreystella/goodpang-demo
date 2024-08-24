from datetime import datetime

from django.db import models


class ServiceUser(models.Model):
    email = models.EmailField()
    order_count = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)  # 낙관적 락을 위한 필드

    class Meta:
        app_label = "user"
        db_table = "service_user"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]

    def create_order_code(self) -> str:  # 초당 1건의 주문만 생성될 수 있게(따닥 방지)
        return datetime.utcnow().strftime("%Y%m%d-%H%M%S") + f"-{self.id}"
