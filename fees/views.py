from django.shortcuts import get_object_or_404, redirect, render
from .forms import FeeForm
from .models import Fee
from academics.models import Course
from students.models import Student


def fee_list(request):
    course_id = request.GET.get("course")
    batch = request.GET.get("batch")

    fees = None

    if course_id and batch:
        fees = Fee.objects.select_related(
            "student",
            "student__course",
        ).filter(
            student__course_id=course_id,
            student__batch=batch,
        )

    courses = Course.objects.all()

    batches = (
        Student.objects
        .values_list("batch", flat=True)
        .distinct()
        .order_by("batch")
    )

    context = {
        "fees": fees,
        "courses": courses,
        "batches": batches,
        "selected_course": course_id,
        "selected_batch": batch,
    }

    return render(request, "fees/fee_list.html", context)


def fee_detail(request, fee_id):
    fee = get_object_or_404(
        Fee.objects.select_related("student"),
        id=fee_id,
    )

    context = {
        "fee": fee,
    }

    return render(request, "fees/fee_detail.html", context)


def fee_create(request):
    if request.method == "POST":
        form = FeeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("fees:fee_list")
    else:
        form = FeeForm()

    context = {
        "form": form,
    }

    return render(request, "fees/fee_form.html", context)

def fee_update(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)

    if request.method == "POST":
        form = FeeForm(request.POST, instance=fee)

        if form.is_valid():
            form.save()
            return redirect("fees:fee_detail", fee_id=fee.id)
    else:
        form = FeeForm(instance=fee)

    context = {
        "form": form,
        "fee": fee,
    }

    return render(request, "fees/fee_form.html", context)

def fee_delete(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)

    if request.method == "POST":
        fee.delete()
        return redirect("fees:fee_list")

    context = {
        "fee": fee,
    }

    return render(request, "fees/fee_confirm_delete.html", context)