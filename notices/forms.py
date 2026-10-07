from django import forms

from .models import Notice


class NoticeForm(forms.ModelForm):

    class Meta:
        model = Notice
        fields = [
            "title",
            "summary",
            "content",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                    "placeholder": "Enter notice title",
                }
            ),
            "summary": forms.TextInput(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                    "placeholder": "Enter a short summary",
                    "maxlength": "300",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": (
                        "w-full px-4 py-3 border border-slate-200 "
                        "rounded-lg outline-none focus:ring-2 "
                        "focus:ring-blue-500 focus:border-blue-500"
                    ),
                    "placeholder": "Write the full notice here...",
                    "rows": 8,
                }
            ),
        }