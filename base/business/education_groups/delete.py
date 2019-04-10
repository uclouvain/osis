##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import ngettext_lazy, ugettext_lazy as _

from base.models.group_element_year import GroupElementYear
from base.models.offer_enrollment import OfferEnrollment


def get_protected_messages_by_education_group_year(education_group_year):
    protected_message = []

    # Count the number of enrollment
    count_enrollment = OfferEnrollment.objects.filter(education_group_year=education_group_year).count()
    if count_enrollment:
        protected_message.append(
            ngettext_lazy(
                "%(count_enrollment)d student is enrolled in the offer.",
                "%(count_enrollment)d students are enrolled in the offer.",
                count_enrollment
            ) % {"count_enrollment": count_enrollment}
        )

    # Check if content is not empty
    if _have_contents(education_group_year):
        protected_message.append(_("The content of the education group is not empty."))

    if education_group_year.linked_with_epc:
        protected_message.append(_("Linked with EPC"))

    return protected_message


def _have_contents(education_group_year):
    return GroupElementYear.objects.filter(parent=education_group_year).exists()
