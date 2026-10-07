from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, teacher_required

from .forms import NoticeForm
from .models import Notice, NoticeRead


@login_required
def notice_list(request):
    notices = Notice.objects.select_related("created_by").all()

    # Opening the Notices page marks all notices as read for teachers.
    if hasattr(request.user, "teacher_profile"):
        NoticeRead.objects.bulk_create(
            [
                NoticeRead(
                    teacher=request.user,
                    notice=notice,
                )
                for notice in notices.exclude(
                    reads__teacher=request.user,
                )
            ],
            ignore_conflicts=True,
        )

    return render(
        request,
        "notices/notice_list.html",
        {
            "notices": notices,
            "base_template": (
                "teacher_base.html"
                if hasattr(request.user, "teacher_profile")
                else "base.html"
            ),
        },
    )


@admin_required
def notice_create(request):
    if request.method == "POST":
        form = NoticeForm(request.POST)

        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()

            messages.success(
                request,
                "Notice published successfully.",
            )

            return redirect("notices:notice_list")

    else:
        form = NoticeForm()

    return render(
        request,
        "notices/notice_form.html",
        {
            "form": form,
        },
    )


@login_required
def notice_detail(request, notice_id):
    notice = get_object_or_404(
        Notice.objects.select_related("created_by"),
        id=notice_id,
    )

    # Opening a notice marks that notice as read for the teacher.
    if hasattr(request.user, "teacher_profile"):
        NoticeRead.objects.get_or_create(
            teacher=request.user,
            notice=notice,
        )

    return render(
        request,
        "notices/notice_detail.html",
        {
            "notice": notice,
            "base_template": (
                "teacher_base.html"
                if hasattr(request.user, "teacher_profile")
                else "base.html"
            ),
        },
    )


@admin_required
def notice_update(request, notice_id):
    notice = get_object_or_404(
        Notice,
        id=notice_id,
    )

    if request.method == "POST":
        form = NoticeForm(
            request.POST,
            instance=notice,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Notice updated successfully.",
            )

            return redirect(
                "notices:notice_detail",
                notice_id=notice.id,
            )

    else:
        form = NoticeForm(instance=notice)

    return render(
        request,
        "notices/notice_form.html",
        {
            "form": form,
            "notice": notice,
        },
    )


@admin_required
def notice_delete(request, notice_id):
    notice = get_object_or_404(
        Notice,
        id=notice_id,
    )

    if request.method == "POST":
        notice.delete()

        messages.success(
            request,
            "Notice deleted successfully.",
        )

        return redirect("notices:notice_list")

    return render(
        request,
        "notices/notice_confirm_delete.html",
        {
            "notice": notice,
        },
    )


@teacher_required
def mark_notifications_read(request):
    if request.method == "POST":
        notices = Notice.objects.all()

        NoticeRead.objects.bulk_create(
            [
                NoticeRead(
                    teacher=request.user,
                    notice=notice,
                )
                for notice in notices.exclude(
                    reads__teacher=request.user,
                )
            ],
            ignore_conflicts=True,
        )

        return JsonResponse({"success": True})

    return JsonResponse(
        {"success": False},
        status=405,
    )