from django.conf import settings
from django.db import models


class Notice(models.Model):
    title = models.CharField(max_length=200)

    summary = models.CharField(
        max_length=300,
        help_text="Short summary shown in notifications.",
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_notices",
    )

    published_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class NoticeRead(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notice_reads",
    )

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name="reads",
    )

    read_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "notice"],
                name="unique_teacher_notice_read",
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.notice.title}"