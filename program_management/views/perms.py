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
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _

from osis_role.errors import get_permission_error


def can_update_group_element_year(user, group_element_year):
    perm = 'base.change_educationgroupcontent'
    result = user.has_perm(perm)
    if not result:
        msg = get_permission_error(user, perm)
        raise PermissionDenied(_(msg))
    return True


def can_detach_group_element_year(user, group_element_year):
    result = user.has_perm('base.detach_educationgroup', group_element_year.parent)
    if not result:
        raise PermissionDenied
    return True
