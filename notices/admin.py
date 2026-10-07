from django.contrib import admin

from .models import Notice, NoticeRead


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_by",
        "published_at",
    )

    search_fields = (
        "title",
        "summary",
        "content",
    )

    list_filter = (
        "published_at",
    )


@admin.register(NoticeRead)
class NoticeReadAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "notice",
        "read_at",
    )

    search_fields = (
        "teacher__username",
        "notice__title",
    )