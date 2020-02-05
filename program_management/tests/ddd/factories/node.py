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

import operator
import random

import factory.fuzzy

from base.models.enums.education_group_types import TrainingType
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from program_management.ddd.domain.node import NodeEducationGroupYear, NodeLearningUnitYear, NodeGroupYear


def generate_group_year_node_id(node):
    if node.create_django_objects_in_db:
        return TrainingFactory(acronym=node.acronym, title=node.title, academic_year__year=node.year).pk
    return random.randint(1, 999999999)


def generate_year(node):
    if node.create_django_objects_in_db:
        return AcademicYearFactory().year
    return random.randint(1999, 2099)


class NodeFactory(factory.Factory):
    acronym = factory.Sequence(lambda n: 'Acrony%02d' % n)
    title = factory.fuzzy.FuzzyText(length=240)
    year = factory.LazyAttribute(generate_year)

    create_django_objects_in_db = False

    # @factory.post_generation
    # def __remove_unused(self):
    #     delattr(self, 'create_django_objects_in_db')


class NodeEducationGroupYearFactory(NodeFactory):
    class Meta:
        model = NodeEducationGroupYear
        abstract = False
    node_id = factory.LazyAttribute(generate_group_year_node_id)
    node_type = factory.fuzzy.FuzzyChoice(TrainingType)
    children = None


class NodeGroupYearFactory(NodeFactory):

    class Meta:
        model = NodeGroupYear
        abstract = False

    node_id = factory.LazyAttribute(generate_group_year_node_id)
    node_type = factory.fuzzy.FuzzyChoice(TrainingType)
    children = None


def generate_learning_unit_year_node_id(node):
    if node.create_django_objects_in_db:
        return LearningUnitYearFactory(
            acronym=node.acronym,
            specific_title=node.title,
            academic_year__year=node.year
        ).pk
    return random.randint(1, 999999999)


class NodeLearningUnitYearFactory(NodeFactory):

    class Meta:
        model = NodeLearningUnitYear
        abstract = False

    node_id = factory.LazyAttribute(generate_learning_unit_year_node_id)
    node_type = None
