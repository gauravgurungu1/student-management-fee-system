from decimal import Decimal

from django.db import models
from django.db.models import Sum

from students.models import Student


class Fee(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fees",
    )

    title = models.CharField(max_length=100)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    due_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.title}"

    @property
    def total_paid(self):
        return self.payments.filter(
            status="COMPLETED"
        ).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

    @property
    def remaining_amount(self):
        remaining = self.amount - self.total_paid

        if remaining < 0:
            return Decimal("0")

        return remaining

    @property
    def computed_status(self):
        paid = self.total_paid

        if paid == 0:
            return "PENDING"

        if paid < self.amount:
            return "PARTIAL"

        return "PAID"