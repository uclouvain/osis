from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadContent(TrainingRead):
    template_name = "training/content_read.html"
    active_tab = Tab.CONTENT

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "children": self.get_object().children
        }
