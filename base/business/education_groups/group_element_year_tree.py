##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db.models import OuterRef, Exists
from django.urls import reverse

from base.business.group_element_years.management import EDUCATION_GROUP_YEAR, LEARNING_UNIT_YEAR
from base.models.prerequisite import Prerequisite


class NodeBranchJsTree:
    """ Use to generate json from a list of education group years compatible with jstree """
    element_type = EDUCATION_GROUP_YEAR

    def __init__(self, root, group_element_year=None):
        self.root = root
        self.group_element_year = group_element_year
        self.children = self.generate_children()

    def generate_children(self):
        result = []
        for group_element_year in self.get_queryset():
            if group_element_year.child_branch and group_element_year.child_branch != self.root:
                result.append(NodeBranchJsTree(self.root, group_element_year))
            elif group_element_year.child_leaf:
                result.append(NodeLeafJsTree(self.root, group_element_year))

        return result

    def get_queryset(self):
        has_prerequisite = Prerequisite.objects.filter(
            education_group_year__id=self.root.id,
            learning_unit_year__id=OuterRef("child_leaf__id"),
        ).exclude(prerequisite__exact='')

        return self.education_group_year.groupelementyear_set.all() \
            .annotate(has_prerequisites=Exists(has_prerequisite)) \
            .select_related('child_branch__academic_year',
                            'child_leaf__academic_year',
                            'child_leaf__learning_container_year')

    def to_json(self):
        group_element_year_pk = self.group_element_year.pk if self.group_element_year else '#'
        return {
            'text': self.education_group_year.verbose,
            'children': [child.to_json() for child in self.children],
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'element_id': self.education_group_year.pk,
                'element_type': self.element_type,
                'title': self.education_group_year.acronym,
            },
            'id': 'id_{}_{}'.format(self.education_group_year.pk, group_element_year_pk),
        }

    @property
    def education_group_year(self):
        return self.root if not self.group_element_year else self.group_element_year.child_branch

    def url_group_to_parent(self):
        return "?group_to_parent=" + str(self.group_element_year.pk if self.group_element_year else 0)

    def get_url(self):
        url = reverse('education_group_read', args=[self.root.pk, self.education_group_year.pk])
        return url + self.url_group_to_parent()


class NodeLeafJsTree(NodeBranchJsTree):
    """ The leaf has no child """
    element_type = LEARNING_UNIT_YEAR

    @property
    def learning_unit_year(self):
        if self.group_element_year:
            return self.group_element_year.child_leaf

    @property
    def education_group_year(self):
        return

    def to_json(self):
        group_element_year_pk = self.group_element_year.pk if self.group_element_year else '#'
        return {
            'text': self.learning_unit_year.acronym,
            'icon': "glyphicon glyphicon-leaf" if self.group_element_year.has_prerequisites else "jstree-file",
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'element_id': self.learning_unit_year.pk,
                'element_type': self.element_type,
                'title': self.learning_unit_year.complete_title,
            },
            'id': 'id_{}_{}'.format(self.learning_unit_year.pk, group_element_year_pk),
        }

    def get_url(self):
        url = reverse('learning_unit_utilization', args=[self.root.pk, self.learning_unit_year.pk])
        return url + self.url_group_to_parent()

    def generate_children(self):
        return []
