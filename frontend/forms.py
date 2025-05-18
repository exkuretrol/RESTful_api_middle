from django import forms
from django.utils import timezone
from api.models import LeaveCategory
from zoneinfo import ZoneInfo

tz = ZoneInfo("Asia/Taipei")


class LeaveRequestsForm(forms.Form):
    category = forms.ChoiceField(
        choices=LeaveCategory.objects.all().values_list("id", "name"),
        label="假別",
    )
    effective_start_datetime = forms.DateTimeField(
        label="開始時間",
        widget=forms.HiddenInput(),
        initial=timezone.now()
        .astimezone(tz)
        .replace(hour=9, minute=0, second=0, microsecond=0),
    )

    effective_end_datetime = forms.DateTimeField(
        label="結束時間",
        widget=forms.HiddenInput(),
        initial=timezone.now()
        .astimezone(tz)
        .replace(hour=18, minute=0, second=0, microsecond=0),
    )

    reason = forms.CharField(
        label="請假事由",
        max_length=255,
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )
