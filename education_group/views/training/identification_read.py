##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from reversion.models import Version

from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_certificate_aim import EducationGroupCertificateAim
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.models.education_group_organization import EducationGroupOrganization
from base.models.education_group_year_domain import EducationGroupYearDomain
from education_group.ddd.command import GetTrainingEmptyFieldsOnWarningCommand
from education_group.ddd.domain import exception
from education_group.ddd.service.read.check_training_empty_fields_on_warning_service import \
    check_training_empty_fields_on_warning
from education_group.models.group_year import GroupYear
from education_group.views.training.common_read import TrainingRead, Tab
from program_management.models.education_group_version import EducationGroupVersion


class TrainingReadIdentification(TrainingRead):
    template_name = "education_group_app/training/identification_read.html"
    active_tab = Tab.IDENTIFICATION

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "permission_object": self.get_permission_object(),
            "history": self.get_related_history(),
            "fields_warnings": self.get_fields_in_warning()
        }

    def get_fields_in_warning(self) -> List[str]:
        if self.current_version.is_official_standard:
            try:
                cmd = GetTrainingEmptyFieldsOnWarningCommand(acronym=self.training.acronym, year=self.training.year)
                check_training_empty_fields_on_warning(cmd)
            except exception.TrainingEmptyFieldException as e:
                return e.fields
        return []

    def get_related_history(self):
        group_year = self.education_group_version.root_group
        versions = Version.objects.get_for_object(
            self.education_group_version
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
            serialized_data__contains="\"pk\": {}".format(group_year.pk)
        )

        return versions.order_by('-revision__date_created').distinct('revision__date_created')
