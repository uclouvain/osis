from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadDiplomaCertificate(TrainingRead):
    template_name = "training/diplomas_certificates_read.html"
    active_tab = Tab.DIPLOMAS_CERTIFICATES

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
