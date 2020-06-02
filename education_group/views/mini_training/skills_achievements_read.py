import functools

from django.shortcuts import redirect
from django.urls import reverse

from base.business.education_groups import general_information_sections
from education_group.views.mini_training.common_read import MiniTrainingRead, Tab
from education_group.views.serializers import achievement


class MiniTrainingReadSkillsAchievements(MiniTrainingRead):
    template_name = "mini_training/skills_achievements_read.html"
    active_tab = Tab.SKILLS_ACHIEVEMENTS

    def get(self, request, *args, **kwargs):
        if not self.have_skills_and_achievements_tab():
            return redirect(reverse('mini_training_identification', kwargs=self.kwargs))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        edition_perm_name = "base.change_admissioncondition"
        return {
            **super().get_context_data(**kwargs),
            "achievements": achievement.get_achievements(self.get_object()),
            "can_edit_information": self.request.user.has_perm(edition_perm_name, self.get_permission_object()),
            "program_aims_label": self.get_program_aims_label(),
            "program_aims_update_url": self.get_program_aims_update_url(),
            "additional_information_skills_label": self.get_additional_information_skills_label(),
            "additional_information_skills_update_url": self.get_additional_information_skills_update_url()
        }

    def get_program_aims_update_url(self):
        mini_training_id = self.get_education_group_version().offer_id
        return reverse('education_group_achievement_program_aim', args=[mini_training_id, mini_training_id])

    def get_program_aims_label(self):
        return next(
            label for label in self.get_translated_labels()
            if label['label_id'] == general_information_sections.CMS_LABEL_PROGRAM_AIM
        )

    def get_additional_information_skills_update_url(self):
        mini_training_id = self.get_education_group_version().offer_id
        return reverse('education_group_achievement_additional_information', args=[mini_training_id, mini_training_id])

    def get_additional_information_skills_label(self):
        return next(
            label for label in self.get_translated_labels()
            if label['label_id'] == general_information_sections.CMS_LABEL_ADDITIONAL_INFORMATION
        )

    @functools.lru_cache()
    def get_translated_labels(self):
        return achievement.get_skills_labels(self.get_object(), self.request.LANGUAGE_CODE)
