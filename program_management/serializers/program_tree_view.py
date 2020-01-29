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
from django.templatetags.static import static
from django.urls import reverse
from rest_framework import serializers

from backoffice.settings.rest_framework import utils
from base.models.enums import link_type
from program_management.domain import program_tree, link, node
from program_management.models.enums import node_type


class NodeViewAttributeSerializer(serializers.Serializer):
    href = serializers.SerializerMethodField()
    root = serializers.SerializerMethodField()
    element_id = serializers.IntegerField(source='child.pk')
    element_type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    attach_url = serializers.SerializerMethodField()
    detach_url = serializers.SerializerMethodField()
    modify_url = serializers.SerializerMethodField()
    attach_disabled = serializers.BooleanField(default=True)
    attach_msg = serializers.CharField(default=None)
    detach_disabled = serializers.BooleanField(default=True)
    detach_msg = serializers.CharField(default=None)
    modification_disabled = serializers.BooleanField(default=True)
    modification_msg = serializers.CharField(default=None)
    search_url = serializers.SerializerMethodField()

    def get_element_type(self, obj):
        child_node = obj.child

        if isinstance(child_node, node.NodeEducationGroupYear):
            return node_type.EDUCATION_GROUP
        elif isinstance(child_node, node.NodeGroupYear):
            return node_type.GROUP
        elif isinstance(child_node, node.NodeLearningUnitYear):
            return node_type.LEARNING_UNIT
        elif isinstance(child_node, node.NodeLearningClassYear):
            return node_type.LEARNING_CLASS

    def get_root(self, obj: link.Link):
        return self.context['root_id']

    def get_title(self, obj: link.Link):
        child_node = obj.child
        if isinstance(child_node, node.NodeLearningUnitYear):
            return child_node.title
        return child_node.acronym

    def get_href(self, obj: link.Link):
        child_node = obj.child
        return reverse('education_group_read', args=[self.get_root(obj), child_node.pk])  # Fix add table_to_show....

    def get_attach_url(self, obj: link.Link):
        return reverse('education_group_attach', args=[self.get_root(obj), obj.child.pk]),

    def get_detach_url(self, obj: link.Link):
        reverse('group_element_year_delete', args=[
            self.get_root(obj), obj.child.pk, obj.child.pk  #TODO FIX PATH : utiliser le path au lieu de self.group_element_year.pk
        ]) if obj else '#',

    def get_modify_url(self, obj: link.Link):
        reverse('group_element_year_update', args=[
            self.get_root(obj), obj.child.pk, obj.child.pk   #TODO FIX PATH : utiliser le path au lieu de self.group_element_year.pk
        ]) if obj else '#',

    def get_search_url(self, obj: link.Link):
        # if attach.can_attach_learning_units(self.education_group_year):
        #     return reverse('quick_search_learning_unit', args=[self.root.pk, self.education_group_year.pk])
        return reverse('quick_search_education_group', args=[self.get_root(obj), obj.child.pk])


class NodeViewSerializer(serializers.Serializer):
    text = serializers.CharField(source='child.title')
    icon = serializers.SerializerMethodField()
    children = utils.RecursiveField(source='child.children', many=True)
    a_attr = NodeViewAttributeSerializer(source='*')

    def get_icon(self, obj: link.Link):
        if obj.link_type == link_type.LinkTypes.REFERENCE.name:
            return static('img/reference.jpg')
        return None


class ProgramTreeViewSerializer(serializers.Serializer):
    text = serializers.CharField(source='root_node.title')
    icon = serializers.SerializerMethodField()
    children = NodeViewSerializer(source='root_node.children', many=True)

    def __init__(self, instance: program_tree.ProgramTree, **kwargs):
        kwargs['context'] = {
            **kwargs.get('context', {}),
            'root_id': instance.root_node.pk
        }
        super().__init__(instance, **kwargs)

    def get_icon(self, tree: program_tree.ProgramTree):
        return None
