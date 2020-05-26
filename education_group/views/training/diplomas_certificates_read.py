from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadDiplomaCertificate(TrainingRead):
    template_name = "training/diplomas_certificates_read.html"
    active_tab = Tab.DIPLOMAS_CERTIFICATES

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "training": self.get_training(),
        }

    def get_training(self):
        return TrainingRepository.get(TrainingIdentity(acronym=self.get_object().title, year=self.get_object().year))
