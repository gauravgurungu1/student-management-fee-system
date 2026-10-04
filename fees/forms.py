from django import forms
from .models import Fee


class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee

        fields = [
            "student",
            "title",
            "amount",
            "due_date",
        ]

        widgets = {
            "student": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
            }),

            "title": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "e.g. Semester Fee",
            }),

            "amount": forms.NumberInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Enter fee amount",
                "step": "0.01",
            }),

            "due_date": forms.DateInput(attrs={
                "class": "w-full px-4 py-3 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "type": "date",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Student cannot be changed after the fee is created.
        if self.instance and self.instance.pk:
            self.fields["student"].disabled = True