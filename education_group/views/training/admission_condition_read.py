import functools

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

from base.models.enums.education_group_types import TrainingType
from base.utils.cache_keys import get_tab_lang_keys
from base.utils.cache import cache

from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from education_group.views.serializers import admission_condition
from education_group.views.training.common_read import TrainingRead, Tab


class TrainingReadAdmissionCondition(TrainingRead, UserPassesTestMixin):
    template_name = "training/admission_condition_read.html"
    active_tab = Tab.ADMISSION_CONDITION

    def test_func(self):
        return self.get_training().type.name in TrainingType.with_admission_condition()

    def get_context_data(self, **kwargs):
        training = self.get_training()
        context = {
            **super().get_context_data(**kwargs),
            "can_edit_information":
                self.request.user.has_perm("base.change_admissioncondition", self.education_group_version.offer),
            "training": training,
            "common_admission_condition": self.get_common_admission_condition(),
            "admission_condition": self.get_admission_condition(),
        }

        if training.is_master_60_credits() or training.is_master_120_credits() or training.is_master_180_240_credits():
            current_language = cache.get(get_tab_lang_keys(self.request.user)) or settings.LANGUAGE_CODE_FR
            context.update({
                'language': {
                    'list': self.__get_language_list(),
                    'current_language': current_language,
                },
                "admission_condition_lines": self.get_admission_condition_lines(current_language),

                # TODO: Switch to DDD (Use in case of URL on admission_condition_table_row block)
                "education_group_year": self.education_group_version.offer,
                "root": self.education_group_version.offer
            })
        return context

    def __get_language_list(self):
        # TODO : Use sluggify URL
        offer_id = self.education_group_version.offer_id
        return [
            {'text': "fr-be", 'url':  reverse('tab_lang_edit', args=[offer_id, offer_id, 'fr-be'])},
            {'text': "en", 'url': reverse('tab_lang_edit', args=[offer_id, offer_id, 'en'])}
        ]

    @functools.lru_cache()
    def get_training(self):
        return TrainingRepository.get(TrainingIdentity(acronym=self.get_object().title, year=self.get_object().year))

    def get_common_admission_condition(self):
        training = self.get_training()
        return admission_condition.get_common_admission_condition(
            training.type.name,
            training.year
        )

    def get_admission_condition(self):
        training = self.get_training()
        return admission_condition.get_admission_condition(
            training.acronym,
            training.year
        )

    def get_admission_condition_lines(self, language: str):
        training = self.get_training()
        return admission_condition.get_admission_condition_lines(
            training.acronym,
            training.year,
            language
        )
