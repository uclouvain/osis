##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.db.models import Subquery, OuterRef
from django.views.generic import ListView

from base.auth.roles.entity_manager import EntityManager
from base.auth.roles.program_manager import ProgramManager
from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums.groups import TUTOR
from base.models.person import Person


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Person
    ordering = 'last_name', 'first_name', 'global_id'
    permission_required = 'base.can_read_persons_roles'
    raise_exception = True

    def get_queryset(self):
        prefetch_pgm_mgr = Prefetch(
            "programmanager_set",
            queryset=ProgramManager.objects.all().annotate(
                most_recent_acronym=Subquery(
                    EducationGroupYear.objects.filter(
                        education_group=OuterRef('education_group__pk'),
                        academic_year=current_academic_year()
                    ).values('acronym')
                )
            ).order_by('most_recent_acronym')
        )

        prefetch_entity_mgr = Prefetch(
            "base_entitymanager_set",
            queryset=EntityManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

        prefetches = [prefetch_pgm_mgr, prefetch_entity_mgr]
        if 'learning_unit' in settings.INSTALLED_APPS:
            prefetches.append(self.get_central_manager_for_ue())
            prefetches.append(self.get_faculty_manager_for_ue())

        if 'education_group' in settings.INSTALLED_APPS:
            prefetches.append(self.get_central_manager_for_of())
            prefetches.append(self.get_faculty_manager_for_of())

        if 'partnership' in settings.INSTALLED_APPS:
            prefetches.append(self.get_partnership_entity_managers())

        return super().get_queryset().select_related(
                'user'
            ).prefetch_related(
                'user__groups'
            ).prefetch_related(
                *prefetches
            ).filter(
                user__is_active=True,
                user__groups__in=Group.objects.exclude(name=TUTOR)
            ).distinct()

    def get_partnership_entity_managers(self):
        from partnership.auth.roles.partnership_manager import PartnershipEntityManager
        return Prefetch(
            "partnership_partnershipentitymanager_set",
            queryset=PartnershipEntityManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

    def get_faculty_manager_for_ue(self):
        from learning_unit.auth.roles.faculty_manager import FacultyManager
        return Prefetch(
            "learning_unit_facultymanager_set",
            queryset=FacultyManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

    def get_central_manager_for_ue(self):
        from learning_unit.auth.roles.central_manager import CentralManager
        return Prefetch(
            "learning_unit_centralmanager_set",
            queryset=CentralManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

    def get_faculty_manager_for_of(self):
        from education_group.auth.roles.faculty_manager import FacultyManager
        return Prefetch(
            "education_group_facultymanager_set",
            queryset=FacultyManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

    def get_central_manager_for_of(self):
        from education_group.auth.roles.central_manager import CentralManager
        return Prefetch(
            "education_group_centralmanager_set",
            queryset=CentralManager.objects.all().annotate(
                entity_recent_acronym=self._get_most_recent_acronym_subquery()
            ).order_by('entity_recent_acronym')
        )

    def _get_most_recent_acronym_subquery(self):
        return Subquery(
            EntityVersion.objects.filter(
                entity=OuterRef('entity__pk')
            ).order_by('-start_date').values('acronym')[:1]
        )
