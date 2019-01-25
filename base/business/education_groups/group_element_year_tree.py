# ########################################################################################
#  OSIS stands for Open Student Information System. It's an application                  #
#  designed to manage the core business of higher education institutions,                #
#  such as universities, faculties, institutes and professional schools.                 #
#  The core business involves the administration of students, teachers,                  #
#  courses, programs and so on.                                                          #
#                                                                                        #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)    #
#                                                                                        #
#  This program is free software: you can redistribute it and/or modify                  #
#  it under the terms of the GNU General Public License as published by                  #
#  the Free Software Foundation, either version 3 of the License, or                     #
#  (at your option) any later version.                                                   #
#                                                                                        #
#  This program is distributed in the hope that it will be useful,                       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                         #
#  GNU General Public License for more details.                                          #
#                                                                                        #
#  A copy of this license - GNU General Public License - is available                    #
#  at the root of the source code of this program.  If not,                              #
#  see http://www.gnu.org/licenses/.                                                     #
# ########################################################################################
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import OuterRef, Exists
from django.urls import reverse

from base.business.group_element_years.management import EDUCATION_GROUP_YEAR, LEARNING_UNIT_YEAR
from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import build_tree_in_memory, GroupElementYear
from base.models.prerequisite_item import PrerequisiteItem

def instance_NodeBranchJsTree(root):

    has_prerequisite = PrerequisiteItem.objects.filter(
        prerequisite__education_group_year__id=root.id,
        prerequisite__learning_unit_year__id=OuterRef("child_leaf__id"),
    )

    is_prerequisite = PrerequisiteItem.objects.filter(
        learning_unit__learningunityear__id=OuterRef("child_leaf__id"),
        prerequisite__education_group_year=root.id,
    )

    queryset = GroupElementYear.objects.all() \
        .annotate(has_prerequisite=Exists(has_prerequisite)) \
        .annotate(is_prerequisite=Exists(is_prerequisite)) \
        .select_related('child_branch__academic_year',
                        'child_leaf__academic_year',
                        'child_leaf__learning_container_year')
    group_elem_year_instance_by_id = build_tree_in_memory(root, queryset)
    return NodeBranchJsTree(root, cache_group_elements_year=group_elem_year_instance_by_id)


class NodeBranchJsTree:
    """ Use to generate json from a list of education group years compatible with jstree """
    element_type = EDUCATION_GROUP_YEAR

    def __init__(self, root, group_element_year=None, cache_group_elements_year=None):

        self.children = []
        self.root = root
        self.group_element_year = group_element_year
        self.reference = self.group_element_year.link_type == LinkTypes.REFERENCE.name \
            if self.group_element_year else False
        self.icon = self._get_icon()
        self.cache_group_elements_year = cache_group_elements_year or {}
        # build_tree_in_memory(self.education_group_year, self.get_queryset())

        self.generate_children()

    def generate_children(self):
        for group_element_year in self.cache_group_elements_year.get(self.education_group_year.id) or []:
            if group_element_year.child_branch and group_element_year.child_branch != self.root:
                node = NodeBranchJsTree(self.root, group_element_year, cache_group_elements_year=self.cache_group_elements_year)

            elif group_element_year.child_leaf:
                node = NodeLeafJsTree(self.root, group_element_year, cache_group_elements_year=self.cache_group_elements_year)

            else:
                continue

            self.children.append(node)

    def get_queryset(self):
        has_prerequisite = PrerequisiteItem.objects.filter(
            prerequisite__education_group_year__id=self.root.id,
            prerequisite__learning_unit_year__id=OuterRef("child_leaf__id"),
        )

        is_prerequisite = PrerequisiteItem.objects.filter(
            learning_unit__learningunityear__id=OuterRef("child_leaf__id"),
            prerequisite__education_group_year=self.root.id,
        )

        return self.education_group_year.groupelementyear_set.all() \
            .annotate(has_prerequisite=Exists(has_prerequisite)) \
            .annotate(is_prerequisite=Exists(is_prerequisite)) \
            .select_related('child_branch__academic_year',
                            'child_leaf__academic_year',
                            'child_leaf__learning_container_year')

    def to_json(self):
        group_element_year_pk = self.group_element_year.pk if self.group_element_year else '#'
        return {
            'text': self.education_group_year.verbose,
            'icon': self.icon,
            'children': [child.to_json() for child in self.children],
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'element_id': self.education_group_year.pk,
                'element_type': self.element_type,
                'title': self.education_group_year.acronym,
                'attach_url': reverse('education_group_attach', args=[self.root.pk, self.education_group_year.pk]),
                'detach_url': reverse('group_element_year_delete', args=[
                    self.root.pk, self.education_group_year.pk, self.group_element_year.pk
                ]) if self.group_element_year else '#'
            },
            'id': 'id_{}_{}'.format(self.education_group_year.pk, group_element_year_pk),
        }

    def to_list(self):
        """ Generate list of group_element_year without reference link """
        result = []

        for child in self.children:
            child_list = child.to_list()

            if child.reference:
                result.extend(child_list)

            else:
                result.append(child.group_element_year)
                if child_list:
                    result.append(child_list)

        return result

    def _get_icon(self):
        if self.reference:
            return static('img/reference.jpg')

    @property
    def education_group_year(self):
        return self.root if not self.group_element_year else self.group_element_year.child_branch

    def url_group_to_parent(self):
        return "?group_to_parent=" + str(self.group_element_year.pk if self.group_element_year else 0)

    def get_url(self):
        url = reverse('education_group_read', args=[self.root.pk, self.education_group_year.pk])
        return url + self.url_group_to_parent()


class NodeLeafJsTree(NodeBranchJsTree):
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
            'icon': self.icon,
            'a_attr': {
                'href': self.get_url(),
                'root': self.root.pk,
                'group_element_year': self.group_element_year and self.group_element_year.pk,
                'element_id': self.learning_unit_year.pk,
                'element_type': self.element_type,
                'title': self.learning_unit_year.complete_title,
                'has_prerequisite': self.group_element_year.has_prerequisite,
                'is_prerequisite': self.group_element_year.is_prerequisite,
                'detach_url': reverse('group_element_year_delete', args=[
                    self.root.pk, self.group_element_year.parent.pk, self.group_element_year.pk
                ]) if self.group_element_year else '#'
            },
            'id': 'id_{}_{}'.format(self.learning_unit_year.pk, group_element_year_pk),
        }

    def _get_icon(self):
        if self.group_element_year.has_prerequisite and self.group_element_year.is_prerequisite:
            return "fa fa-exchange"
        elif self.group_element_year.has_prerequisite:
            return "fa fa-arrow-right"
        elif self.group_element_year.is_prerequisite:
            return "fa fa-arrow-left"
        return "jstree-file"

    def get_url(self):
        url = reverse('learning_unit_utilization', args=[self.root.pk, self.learning_unit_year.pk])
        return url + self.url_group_to_parent()

    def generate_children(self):
        """ The leaf does not have children """
        return
