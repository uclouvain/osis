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
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from learning_unit.api.serializers.utils import LearningUnitDDDHyperlinkedIdentityField
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.program_tree import ProgramTree


class BaseCommomSerializer(serializers.Serializer):
    title = serializers.SerializerMethodField()
    url = LearningUnitDDDHyperlinkedIdentityField(read_only=True)

    def get_title(self, obj: 'Node'):
        if self.context.get('language') == settings.LANGUAGE_CODE_EN:
            specific_title = obj.specific_title_en
            common_title = obj.common_title_en
        else:
            specific_title = obj.specific_title_fr
            common_title = obj.common_title_fr

        complete_title = specific_title
        if common_title:
            complete_title = common_title + ' - ' + specific_title
        return complete_title


class PrerequisiteItemSerializer(serializers.Serializer):
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    absolute_credits = serializers.SerializerMethodField()
    relative_credits = serializers.SerializerMethodField()
    block = serializers.SerializerMethodField()
    mandatory = serializers.SerializerMethodField()

    program_tree: ProgramTree = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.program_tree = self.context.get('tree')

    def get_title(self, obj: 'PrerequisiteItemGroup'):
        node = self.context.get('tree').get_node_by_code_and_year(obj.prerequisite_items[0].code,
                                                                  obj.prerequisite_items[0].year)
        if self.context.get('language') == settings.LANGUAGE_CODE_EN:
            specific_title = node.specific_title_en
            common_title = node.common_title_en
        else:
            specific_title = node.specific_title_fr
            common_title = node.common_title_fr

        complete_title = specific_title
        if common_title:
            complete_title = common_title + ' - ' + specific_title
        return complete_title

    def get_url(self, obj: 'PrerequisiteItemGroup'):
        request = self.context.get('request')
        view_name = 'learning_unit_api_v1:learningunits_read'
        url_kwargs = {
            'acronym': obj.prerequisite_items[0].code,
            'year': obj.prerequisite_items[0].year
        }
        return request.build_absolute_uri(reverse(view_name, kwargs=url_kwargs))

    def get_code(self, obj: 'PrerequisiteItemGroup'):
        return str(obj)

    def get_absolute_credits(self, obj: 'PrerequisiteItemGroup'):
        node = self.context.get('tree').get_node_by_code_and_year(obj.prerequisite_items[0].code,
                                                                  obj.prerequisite_items[0].year)
        return str(node.credits.to_integral_value())

    def get_relative_credits(self, obj: 'PrerequisiteItemGroup'):
        node = self.context.get('tree').get_node_by_code_and_year(obj.prerequisite_items[0].code,
                                                                  obj.prerequisite_items[0].year)
        links = self.context.get('tree').get_links_using_node(node)
        return " ; ".join(set(["{}".format(grp.relative_credits) for grp in links]))

    def get_block(self, obj: 'PrerequisiteItemGroup'):
        node = self.context.get('tree').get_node_by_code_and_year(obj.prerequisite_items[0].code,
                                                                  obj.prerequisite_items[0].year)
        links = self.context.get('tree').get_links_using_node(node)
        return sorted([int(block) for block in str(grp.block or '')] for grp in links)

    def get_mandatory(self, obj: 'PrerequisiteItemGroup'):
        node = self.context.get('tree').get_node_by_code_and_year(obj.prerequisite_items[0].code,
                                                                  obj.prerequisite_items[0].year)
        links = self.context.get('tree').get_links_using_node(node)
        return " ; ".join(set(["{}".format(grp.is_mandatory) for grp in links]))


class EducationGroupPrerequisitesSerializer(BaseCommomSerializer):
    code = serializers.CharField()
    prerequisites_string = serializers.CharField(source='prerequisite', read_only=True)
    prerequisite = PrerequisiteItemSerializer(many=True, source='prerequisite.prerequisite_item_groups')


