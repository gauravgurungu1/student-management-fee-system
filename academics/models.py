from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.PositiveBigIntegerField(default=4)

    def __str__(self):
        return self.name


class Subject(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10, unique=True)
    semester = models.PositiveSmallIntegerField()
    credit_hours = models.PositiveSmallIntegerField(default=3)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ["semester", "code"]


class Room(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )
    capacity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ("SUNDAY", "Sunday"),
        ("MONDAY", "Monday"),
        ("TUESDAY", "Tuesday"),
        ("WEDNESDAY", "Wednesday"),
        ("THURSDAY", "Thursday"),
        ("FRIDAY", "Friday"),
        ("SATURDAY", "Saturday"),
    ]

    teacher = models.ForeignKey(
        "accounts.Teacher",
        on_delete=models.CASCADE,
        related_name="class_schedules",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="class_schedules",
    )

    batch = models.PositiveSmallIntegerField()

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="class_schedules",
    )

    day = models.CharField(
        max_length=10,
        choices=DAY_CHOICES,
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.subject.code} - "
            f"{self.batch} - "
            f"{self.get_day_display()}"
        )

    class Meta:
        ordering = [
            "start_time",
        ]