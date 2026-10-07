from django import forms
from django import forms
from django.db.models import Q

from accounts.models import Teacher, TeacherAssignment
from students.models import Student
from .models import ClassSchedule, Course, Room, Subject


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "duration_years"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
            "code": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
            "duration_years": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "min": "1",
            }),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["course", "name", "code", "semester", "credit_hours"]
        widgets = {
            "course": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
            "code": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
            "semester": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "min": "1",
            }),
            "credit_hours": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "min": "1",
            }),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "capacity"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "e.g. Room 101 or Lab 1",
            }),
            "capacity": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Optional",
                "min": "1",
            }),
        }

class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = [
            "teacher",
            "subject",
            "batch",
            "room",
            "day",
            "start_time",
            "end_time",
        ]

        widgets = {
            "teacher": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),

            "subject": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),

            "batch": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
                "min": "1",
                "placeholder": "e.g. 2024",
            }),

            "room": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),

            "day": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),

            "start_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),

            "end_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        teacher = cleaned_data.get("teacher")
        subject = cleaned_data.get("subject")
        batch = cleaned_data.get("batch")
        room = cleaned_data.get("room")
        day = cleaned_data.get("day")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if not all([
            teacher,
            subject,
            batch,
            room,
            day,
            start_time,
            end_time,
        ]):
            return cleaned_data

        # -------------------------------------------------
        # 1. End time must be after start time
        # -------------------------------------------------

        if start_time >= end_time:
            raise forms.ValidationError(
                "End time must be later than start time."
            )

        # -------------------------------------------------
        # 2. Teacher must actually be assigned
        #    to this subject and batch
        # -------------------------------------------------

        assignment_exists = TeacherAssignment.objects.filter(
            teacher=teacher,
            subject=subject,
            batch=batch,
        ).exists()

        if not assignment_exists:
            raise forms.ValidationError(
                f"{teacher.name} is not assigned to "
                f"{subject.name} for batch {batch}."
            )

        # -------------------------------------------------
        # Common overlapping schedule query
        #
        # Two classes overlap when:
        #
        # existing.start < new.end
        # AND
        # existing.end > new.start
        # -------------------------------------------------

        overlapping = ClassSchedule.objects.filter(
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        # Don't compare the schedule with itself while editing.
        if self.instance and self.instance.pk:
            overlapping = overlapping.exclude(
                pk=self.instance.pk
            )

        # -------------------------------------------------
        # 3. Teacher conflict
        # -------------------------------------------------

        if overlapping.filter(
            teacher=teacher
        ).exists():
            raise forms.ValidationError(
                f"{teacher.name} already has another class "
                f"scheduled during this time."
            )

        # -------------------------------------------------
        # 4. Room conflict
        # -------------------------------------------------

        if overlapping.filter(
            room=room
        ).exists():
            raise forms.ValidationError(
                f"{room.name} is already occupied "
                f"during this time."
            )

        # -------------------------------------------------
        # 5. Batch conflict
        #
        # Same course + same batch cannot have
        # two classes at the same time.
        # -------------------------------------------------

        if overlapping.filter(
            subject__course=subject.course,
            batch=batch,
        ).exists():
            raise forms.ValidationError(
                f"Batch {batch} already has another class "
                f"scheduled during this time."
            )

        # -------------------------------------------------
        # 6. Room capacity check
        # -------------------------------------------------

        if room.capacity:
            student_count = Student.objects.filter(
                course=subject.course,
                batch=batch,
            ).count()

            if student_count > room.capacity:
                raise forms.ValidationError(
                    f"{room.name} has a capacity of "
                    f"{room.capacity}, but batch {batch} "
                    f"has {student_count} students."
                )

        return cleaned_data