from decimal import Decimal

from django import forms
from django.db.models import Sum

from .models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = [
            "fee",
            "amount",
            "payment_method",
        ]

        widgets = {
            "fee": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Enter payment amount",
                "step": "0.01",
                "min": "0.01",
            }),
            "payment_method": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show fees that still have an outstanding balance.
        available_fees = []

        for fee in self.fields["fee"].queryset.select_related("student"):
            if fee.remaining_amount > 0:
                available_fees.append(fee)

        self.fields["fee"].queryset = self.fields["fee"].queryset.filter(
            id__in=[fee.id for fee in available_fees]
        )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        fee = self.cleaned_data.get("fee")

        if not fee:
            return amount

        existing_payments = fee.payments.filter(
            status="COMPLETED"
        )

        # When editing an existing payment, exclude itself.
        if self.instance and self.instance.pk:
            existing_payments = existing_payments.exclude(
                pk=self.instance.pk
            )

        paid = existing_payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

        remaining = fee.amount - paid

        if remaining <= 0:
            raise forms.ValidationError(
                "This fee has already been fully paid."
            )

        if amount > remaining:
            raise forms.ValidationError(
                f"Maximum payable amount is Rs. {remaining}."
            )

        return amount