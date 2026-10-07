from django import forms

from .models import TeacherAssignment


class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ["teacher", "subject", "batch"]

        widgets = {
            "teacher": forms.Select(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                }
            ),
            "subject": forms.Select(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                }
            ),
            "batch": forms.NumberInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                    "placeholder": "e.g. 2026",
                    "min": "1",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        teacher = cleaned_data.get("teacher")
        subject = cleaned_data.get("subject")
        batch = cleaned_data.get("batch")

        if teacher and subject and batch:
            exists = TeacherAssignment.objects.filter(
                teacher=teacher,
                subject=subject,
                batch=batch,
            ).exists()

            if self.instance.pk:
                exists = TeacherAssignment.objects.filter(
                    teacher=teacher,
                    subject=subject,
                    batch=batch,
                ).exclude(
                    pk=self.instance.pk
                ).exists()

            if exists:
                raise forms.ValidationError(
                    "This teacher is already assigned to "
                    "this subject and batch."
                )

        return cleaned_data