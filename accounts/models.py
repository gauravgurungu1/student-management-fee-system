from django.conf import settings
from django.db import models

from academics.models import Subject


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=15,
        unique=True,
    )

    password_set = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    batch = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject", "batch"],
                name="unique_teacher_subject_batch",
            )
        ]
        ordering = ["teacher__name", "subject__code", "batch"]

    def __str__(self):
        return (
            f"{self.teacher.name} - "
            f"{self.subject.code} - "
            f"Batch {self.batch}"
        )