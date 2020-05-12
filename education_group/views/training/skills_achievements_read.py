from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadSkillsAchievements(TrainingRead):
    template_name = "training/skills_achievements_read.html"
    active_tab = Tab.SKILLS_ACHIEVEMENTS

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
