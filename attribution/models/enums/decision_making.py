##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum


PROGRAM_MODIFICATION = "PROGRAM_MODIFICATION"
DISCHARGE = "DISCHARGE"
TEACHING_SUPPLY = "TEACHING_SUPPLY"
AUTHORITY_OR_SABBATICAL_TEACHING_SUPPLY = "AUTHORITY_OR_SABBATICAL_TEACHING_SUPPLY"
DEMAND_FOR_DISCHARGE = "DEMAND_FOR_DISCHARGE"
DEMAND_FOR_CO_HOLDER = "DEMAND_FOR_CO_HOLDER"
CO_HOLDER = "CO_HOLDER"
TO_DELETE = "TO_DELETE"
PART_TIME_TEACHING_SUPPLY = "PART_TIME_TEACHING_SUPPLY"


class DecisionMakings(ChoiceEnum):
    PROGRAM_MODIFICATION = _("Program modification")
    DISCHARGE = _("Discharge")
    TEACHING_SUPPLY = _("Teaching supply")
    AUTHORITY_OR_SABBATICAL_TEACHING_SUPPLY = _("Authority/sabbatical teaching supply")
    DEMAND_FOR_DISCHARGE = _("Demand for discharge")
    DEMAND_FOR_CO_HOLDER = _("Demand for co-holder")
    CO_HOLDER = _("Co-holder")
    TO_DELETE = _("To delete")
    PART_TIME_TEACHING_SUPPLY = _("Part-time teaching supply")
