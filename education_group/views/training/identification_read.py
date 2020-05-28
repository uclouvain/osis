from typing import List

from django.utils.functional import cached_property
from reversion.models import Version

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_certificate_aim import EducationGroupCertificateAim
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.models.education_group_organization import EducationGroupOrganization
from base.models.education_group_year_domain import EducationGroupYearDomain
from education_group.ddd.domain.training import TrainingIdentity
from education_group.ddd.repository.training import TrainingRepository
from education_group.models.group_year import GroupYear
from education_group.views.training.common_read import TrainingRead, Tab
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.business_types import *
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.models.education_group_version import EducationGroupVersion


class TrainingReadIdentification(TrainingRead):
    template_name = "training/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "all_versions_available": self.all_versions_available,
            "current_version": self.current_version,
            "education_group_year": self.get_training(),
            "history": self.get_related_history(),
        }

    @cached_property
    def all_versions_available(self) -> List['ProgramTreeVersion']:
        return ProgramTreeVersionRepository.search_all_versions_from_root_node(
            NodeIdentity(self.get_tree().root_node.code, self.get_tree().root_node.year)
        )

    def get_related_history(self):
        education_group_year = self.education_group_version.offer
        versions = Version.objects.get_for_object(
            education_group_year
        ).select_related('revision__user__person')

        related_models = [
            EducationGroupOrganization,
            EducationGroupAchievement,
            EducationGroupDetailedAchievement,
            EducationGroupYearDomain,
            EducationGroupCertificateAim,
            EducationGroupVersion,
            GroupYear,
        ]

        subversion = Version.objects.none()
        for model in related_models:
            subversion |= Version.objects.get_for_model(model).select_related('revision__user__person')

        versions |= subversion.filter(
            serialized_data__contains="\"education_group_year\": {}".format(education_group_year.pk)
        )

        return versions.order_by('-revision__date_created').distinct('revision__date_created')

    def get_training(self):
        return TrainingRepository.get(TrainingIdentity(acronym=self.get_object().title, year=self.get_object().year))
