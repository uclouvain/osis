from education_group.views.mini_training.common_read import MiniTrainingRead, Tab


class MiniTrainingReadAdmissionCondition(MiniTrainingRead):
    template_name = "mini_training/admission_condition_read.html"
    active_tab = Tab.ADMISSION_CONDITION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
