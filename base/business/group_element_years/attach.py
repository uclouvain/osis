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
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ngettext

from base.business.education_groups.group_element_year_tree import EducationGroupHierarchy
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import MiniTrainingType, TrainingType
from base.models.learning_unit_year import LearningUnitYear


class AttachStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_valid(self):
        pass


class AttachEducationGroupYearStrategy(AttachStrategy):
    def __init__(self, parent: EducationGroupYear, child: EducationGroupYear):
        self.parent = parent
        self.child = child

    @cached_property
    def parents(self):
        return EducationGroupYear.hierarchy.filter(pk=self.parent.pk).get_parents() \
                                           .select_related('education_group_type')

    def is_valid(self):
        if self.parent.education_group_type.name in TrainingType.finality_types() or \
                self.parents.filter(education_group_type__name__in=TrainingType.finality_types()).exists():
            self._check_attach_options_rules()
        if self.parent.education_group_type.name in TrainingType.root_master_2m_types() or \
                self.parents.filter(education_group_type__name__in=TrainingType.root_master_2m_types()).exists():
            self._check_end_year_constraints_on_2m()
        return True

    def _check_end_year_constraints_on_2m(self):
        """
        In context of 2M, when we add a finality [or group which contains finality], we must ensure that
        the end date of all 2M is greater or equals of all finalities
        """
        finalities_to_add_qs = EducationGroupYear.objects.filter(pk=self.child.pk) | \
            EducationGroupYear.hierarchy.filter(pk=self.child.pk).get_children()
        finalities_to_add_qs = finalities_to_add_qs.filter(education_group_type__name__in=TrainingType.finality_types())

        root_2m_qs = self.parents | EducationGroupYear.objects.filter(pk=self.parent.pk)
        root_2m_qs = root_2m_qs.filter(
            education_group_type__name__in=TrainingType.root_master_2m_types(),
            education_group__end_year__isnull=False,
        ).order_by('education_group__end_year')

        errors = []
        if finalities_to_add_qs.exists() and root_2m_qs.exists():
            root_2m_early_end_date = root_2m_qs.first()
            invalid_finalities_acronyms = finalities_to_add_qs.filter(
                Q(education_group__end_year__gt=root_2m_early_end_date.education_group.end_year) |
                Q(education_group__end_year__isnull=True)
            ).values_list('acronym', flat=True)

            if invalid_finalities_acronyms:
                errors.append(
                    ValidationError(
                        ngettext(
                            "Finality \"%(acronym)s\" has an end date greater than %(root_acronym)s program.",
                            "Finalities \"%(acronym)s\" have an end date greater than %(root_acronym)s program.",
                            len(invalid_finalities_acronyms)
                        ) % {
                            "acronym": ', '.join(invalid_finalities_acronyms),
                            "root_acronym": root_2m_early_end_date.acronym
                        }
                    )
                )

        if errors:
            raise ValidationError(errors)

    def _check_attach_options_rules(self):
        """
        In context of MA/MD/MS when we add an option [or group which contains options],
        this options must exist in parent context (2m)
        """
        options_to_add = EducationGroupHierarchy(root=self.child).get_option_list()
        if self.child.education_group_type.name == MiniTrainingType.OPTION.name:
            options_to_add += [self.child]

        errors = []
        for root in self.parents.filter(education_group_type__name__in=[TrainingType.PGRM_MASTER_120.name,
                                                                        TrainingType.PGRM_MASTER_180_240.name]):
            options_in_2m = EducationGroupHierarchy(root=root).get_option_list()
            missing_options = set(options_to_add) - set(options_in_2m)

            if missing_options:
                errors.append(
                    ValidationError(
                        ngettext(
                            "Option \"%(acronym)s\" must be present in %(root_acronym)s program.",
                            "Options \"%(acronym)s\" must be present in %(root_acronym)s program.",
                            len(missing_options)
                        ) % {
                            "acronym": ', '.join(option.acronym for option in missing_options),
                            "root_acronym": root.acronym
                        })
                )
        if errors:
            raise ValidationError(errors)


class AttachLearningUnitYearStrategy(AttachStrategy):
    def __init__(self, parent: EducationGroupYear, child: LearningUnitYear):
        self.parent = parent
        self.child = child

    def is_valid(self):
        return True
