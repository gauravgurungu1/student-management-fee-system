from django.shortcuts import get_object_or_404, redirect, render

from .forms import PaymentForm
from .models import Payment
from accounts.decorators import admin_required


@admin_required
def payment_list(request):
    payments = Payment.objects.select_related(
        "fee",
        "fee__student",
    ).all()

    context = {
        "payments": payments,
    }

    return render(request, "payments/payment_list.html", context)


@admin_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related(
            "fee",
            "fee__student",
        ),
        id=payment_id,
    )

    context = {
        "payment": payment,
    }

    return render(request, "payments/payment_detail.html", context)


@admin_required
def payment_create(request):
    fee_id = request.GET.get("fee")

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save()
            return redirect(
                "payments:payment_detail",
                payment_id=payment.id,
            )

    else:
        form = PaymentForm()

        if fee_id:
            form.fields["fee"].initial = fee_id

    return render(
        request,
        "payments/payment_form.html",
        {"form": form},
    )


@admin_required
def payment_update(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)

        if form.is_valid():
            form.save()
            return redirect(
                "payments:payment_detail",
                payment_id=payment.id,
            )
    else:
        form = PaymentForm(instance=payment)

    context = {
        "form": form,
        "payment": payment,
    }

    return render(request, "payments/payment_form.html", context)


@admin_required
def payment_delete(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == "POST":
        payment.delete()
        return redirect("payments:payment_list")

    context = {
        "payment": payment,
    }

    return render(
        request,
        "payments/payment_confirm_delete.html",
        context,
    )