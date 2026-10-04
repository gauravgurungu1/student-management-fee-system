from django.db import models
from django.utils import timezone
import uuid

from fees.models import Fee


def generate_payment_reference():
    date = timezone.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:8].upper()
    return f"PAY-{date}-{random_part}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("KHALTI", "Khalti"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
    )

    payment_reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            date = timezone.now().strftime("%Y%m%d")
            random_part = uuid.uuid4().hex[:8].upper()
            self.payment_reference = f"PAY-{date}-{random_part}"

        if self.payment_method in {"CASH", "BANK"}:
            self.status = "COMPLETED"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_reference} - {self.fee.student.name}"