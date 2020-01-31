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
from program_management.domain.authorized_relationship import AuthorizedRelationshipList, AuthorizedRelationship
from base.models.authorized_relationship import AuthorizedRelationship as ModelRelationship
from django.db.models import Case, Value, F, When, IntegerField, CharField, Subquery, OuterRef


def fetch() -> AuthorizedRelationshipList:
    authorized_relationships = []
    qs = ModelRelationship.objects.all().annotate(
        parent_type=F('parent_type__name'),
        child_type=F('child_type__name'),
        min_constraint=F('min_count_authorized'),
        max_constraint=F('max_count_authorized'),
    )
    for obj in qs:
        authorized_relationships.append(
            AuthorizedRelationship(
                obj.parent_type,
                obj.child_type,
                obj.min_constraint,
                obj.max_constraint,
            )
        )
    return AuthorizedRelationshipList(authorized_relationships)
