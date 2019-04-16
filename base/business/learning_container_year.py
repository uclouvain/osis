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
from django.utils.translation import ugettext_lazy as _

from base.business import learning_unit_year_with_context
from base.models.enums import learning_unit_year_subtypes


def get_learning_container_year_warnings(learning_container_year):
    _warnings = []
    learning_unit_years_with_context = \
        learning_unit_year_with_context.get_with_context(learning_container_year_id=learning_container_year.id)

    luy_full = next(luy for luy in learning_unit_years_with_context
                    if luy.subtype == learning_unit_year_subtypes.FULL)
    luy_partims = [luy for luy in learning_unit_years_with_context
                   if luy.subtype == learning_unit_year_subtypes.PARTIM]

    if any(volumes_are_inconsistent_between_partim_and_full(partim, luy_full) for partim in luy_partims):
        _warnings.append("{} ({})".format(
            _('Volumes are inconsistent'),
            _('At least a partim volume value is greater than corresponding volume of parent')
        ))
    return _warnings


def volumes_are_inconsistent_between_partim_and_full(partim, full):
    for full_component, full_component_values in full.components.items():
        if any(volumes_are_inconsistent_between_components(partim_component_values, full_component_values)
                for partim_component, partim_component_values in partim.components.items()
                if partim_component.type == full_component.type):
            return True
    return False


def volumes_are_inconsistent_between_components(partim_component_values, full_component_values):
    return any(partim_component_values.get(key) > full_value for key, full_value in full_component_values.items())
