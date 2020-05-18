from django.views.generic import TemplateView

from osis_role.contrib.views import PermissionRequiredMixin


class CommonAggregateAdmissionCondition(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = 'base.view_educationgroup'
    raise_exception = True

    template_name = ""

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
