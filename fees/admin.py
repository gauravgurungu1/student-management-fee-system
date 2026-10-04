from django.contrib import admin
from .models import Fee


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "title",
        "amount",
        "total_paid",
        "remaining_amount",
        "computed_status",
        "due_date",
    )

    list_filter = (
        "due_date",
    )

    search_fields = (
        "student__name",
        "student__email",
        "title",
    )