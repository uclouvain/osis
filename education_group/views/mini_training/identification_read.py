from reversion.models import Version

from education_group.views.mini_training.common_read import MiniTrainingRead, Tab


class MiniTrainingReadIdentification(MiniTrainingRead):
    template_name = "mini_training/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            # "versions": self.get_related_versions(),
        }

    def get_related_versions(self):
        return Version.objects.none()
