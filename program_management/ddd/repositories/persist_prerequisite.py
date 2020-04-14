# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.db import transaction

from base.models import education_group_year, learning_unit_year, prerequisite_item, learning_unit
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.prerequisite import Prerequisite
from base.models import prerequisite as prerequisite_db


@transaction.atomic
def persist(root_node: Node, node: Node, prerequisite: Prerequisite) -> None:
    root_education_group_year = education_group_year.EducationGroupYear.objects.get(id=root_node.node_id)
    node_learning_unit = learning_unit_year.LearningUnitYear.objects.get(id=node.node_id)

    prerequisite_obj, created = prerequisite_db.Prerequisite.objects.get_or_create(
        education_group_year=root_education_group_year,
        learning_unit_year=node_learning_unit,
        defaults={"main_operator": prerequisite.main_operator}
    )
    _delete_old_items(prerequisite_obj)
    _persist_prerequisite_items(prerequisite_obj, prerequisite)


def _persist_prerequisite_items(prerequisite_db_obj, prerequisite: Prerequisite):
    for group_number, group in enumerate(prerequisite.prerequisite_item_groups, 1):
        for position, code in enumerate(group.prerequisite_items, 1):
            learning_unit_obj = get_by_acronym_with_highest_academic_year(code)
            prerequisite_item.PrerequisiteItem.objects.create(
                prerequisite=prerequisite_db_obj,
                learning_unit=learning_unit_obj,
                group_number=group_number,
                position=position,
            )


def get_by_acronym_with_highest_academic_year(acronym):
    return learning_unit.LearningUnit.objects.filter(
        learningunityear__acronym=acronym
    ).order_by(
        'learningunityear__academic_year__year'
    ).last()


def _delete_old_items(prerequisite_db):
    items = prerequisite_db.prerequisiteitem_set.all()
    for item in items:
        item.delete()
