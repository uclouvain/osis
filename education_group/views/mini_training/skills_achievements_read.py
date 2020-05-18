import functools

from base.business.education_groups import general_information_sections
from education_group.views.mini_training.common_read import MiniTrainingRead, Tab
from education_group.views.serializers import achievement


class MiniTrainingReadSkillsAchievements(MiniTrainingRead):
    template_name = "mini_training/skills_achievements_read.html"
    active_tab = Tab.SKILLS_ACHIEVEMENTS

    def get_context_data(self, **kwargs):
        edition_perm_name = "base.change_admissioncondition"
        return {
            **super().get_context_data(**kwargs),
            "achievements": achievement.get_achievements(self.get_object()),
            "can_edit_information": self.request.user.has_perm(edition_perm_name, self.get_permission_object()),
            "program_aims_label": self.get_program_aims_label(),
            "additional_information_skills_label": self.get_additional_information_skills_label(),
        }

    def get_program_aims_label(self):
        return next(
            label for label in self.get_translated_labels()
            if label['label_id'] == general_information_sections.CMS_LABEL_PROGRAM_AIM
        )

    def get_additional_information_skills_label(self):
        return next(
            label for label in self.get_translated_labels()
            if label['label_id'] == general_information_sections.CMS_LABEL_ADDITIONAL_INFORMATION
        )

    @functools.lru_cache()
    def get_translated_labels(self):
        return achievement.get_skills_labels(self.get_object(), self.request.LANGUAGE_CODE)
