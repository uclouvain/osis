from education_group.views.mini_training.common_read import MiniTrainingRead, Tab


class MiniTrainingReadSkillsAchievements(MiniTrainingRead):
    template_name = "mini_training/skills_achievements_read.html"
    active_tab = Tab.SKILLS_ACHIEVEMENTS

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }
