##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import abc

from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from base.business.education_groups.group_element_year_tree import EducationGroupHierarchy
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from base.models.group_element_year import GroupElementYear


class DetachStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_valid(self):
        pass


class DetachEducationGroupYearStrategy(DetachStrategy):
    def __init__(self, link: GroupElementYear):
        self.parent = link.parent
        self.child = link.child

    @cached_property
    def parents(self):
        return EducationGroupYear.hierarchy.filter(pk=self.child.pk).get_parents()\
                                           .select_related('education_group_type')

    def _get_parents_pgrm_master(self):
        return self.parents.filter(education_group_type__name__in=[
            TrainingType.PGRM_MASTER_120.name, TrainingType.PGRM_MASTER_180_240.name])

    def _get_parents_finality_type(self):
        return self.parents.filter(education_group_type__name__in=TrainingType.finality_types())

    def is_valid(self):
        if not self._get_parents_finality_type().exists() and self._get_parents_pgrm_master().exists():
            self._check_detatch_options_rules()
        return True

    def _check_detatch_options_rules(self):
        """
        In context of 2M when we detatch an option [or group which contains option], we must ensure that
        these options are not present in MA/MD/MS
        """
        options_to_detatch = EducationGroupHierarchy(root=self.child).get_option_list()
        if self.child.education_group_type.name == MiniTrainingType.OPTION.name:
            options_to_detatch += [self.child]

        mandatory_options = {
            finality.acronym: EducationGroupHierarchy(root=finality).get_option_list()
            for finality in self._get_parents_finality_type()
        }

        errors = []
        for finality_acronym, options_list in mandatory_options.items():
            missing_options = set(options_list) - set(options_to_detatch)
            if missing_options:
                errors.append(
                    ValidationError(_("Option \"%(acronym)s\" cannot be removed because it is contained in"
                                      " %(finality_acronym)s program.") % {
                        "acronym": ', '.join(option.acronym for option in missing_options),
                        "finality_acronym": finality_acronym
                     })
                )

        if errors:
            raise ValidationError(errors)


class DetachLearningUnitYearStrategy(DetachStrategy):
    def __init__(self, link: GroupElementYear):
        self.parent = link.parent
        self.child = link.child

    def is_valid(self):
        return True
