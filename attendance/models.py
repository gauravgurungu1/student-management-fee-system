from django.conf import settings
from django.db import models

from academics.models import Course, Subject
from students.models import Student


class AttendanceSession(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )

    batch = models.PositiveSmallIntegerField()

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )

    date = models.DateField()

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "batch", "date"],
                name="unique_attendance_session",
            )
        ]

    def __str__(self):
        return (
            f"{self.subject.code} - "
            f"Batch {self.batch} - "
            f"{self.date}"
        )


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="records",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PRESENT",
    )

    marked_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "student"],
                name="unique_attendance_student",
            )
        ]
        ordering = ["student__name"]

    def __str__(self):
        return (
            f"{self.student.name} - "
            f"{self.session.subject.code} - "
            f"{self.status}"
        )