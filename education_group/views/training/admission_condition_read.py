from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadAdmissionCondition(TrainingRead):
    template_name = "training/admission_condition_read.html"
    active_tab = Tab.ADMISSION_CONDITION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
