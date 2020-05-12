from education_group.views.mini_training.common_read import MiniTrainingRead, Tab


class MiniTrainingReadContent(MiniTrainingRead):
    template_name = "mini_training/content_read.html"
    active_tab = Tab.CONTENT

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "children": self.get_object().children
        }
