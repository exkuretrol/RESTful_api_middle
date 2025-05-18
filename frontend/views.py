from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from api.models import LeaveRequest
from .forms import LeaveRequestsForm


class LeaveRequestsView(LoginRequiredMixin, TemplateView):
    template_name = "leaves.html"

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        context["leave_requests_form"] = LeaveRequestsForm()
        context["leaves"] = LeaveRequest.objects.filter(request_user=self.request.user)
        return context
