# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction, Error
from django.db.models import Q, F, Max
from django.utils.translation import ugettext as _

from base.business.education_groups.create import create_initial_group_element_year_structure
from base.business.education_groups.postponement import duplicate_education_group_year, ConsistencyError
from base.business.utils.postponement import AutomaticPostponement
from base.models.academic_year import AcademicYear
from base.models.education_group import EducationGroup
from base.models.enums.education_group_categories import TRAINING
from base.models.enums.education_group_types import MiniTrainingType
from base.utils.send_mail import send_mail_before_annual_procedure_of_automatic_postponement_of_egy, \
    send_mail_after_annual_procedure_of_automatic_postponement_of_egy


class EducationGroupAutomaticPostponement(AutomaticPostponement):
    model = EducationGroup

    send_before = send_mail_before_annual_procedure_of_automatic_postponement_of_egy
    send_after = send_mail_after_annual_procedure_of_automatic_postponement_of_egy
    extend_method = duplicate_education_group_year
    msg_result = _("%(number_extended)s education group(s) extended and %(number_error)s error(s)")

    def get_queryset(self, queryset=None):
        # We need to postpone only trainings and some mini trainings
        if not queryset:
            queryset = self.model.objects.all()

        return queryset.filter(
            Q(educationgroupyear__education_group_type__category=TRAINING) |
            Q(educationgroupyear__education_group_type__name__in=MiniTrainingType.to_postpone())
        ).annotate(
            last_year=Max('educationgroupyear__academic_year__year')
        )

    def get_already_duplicated(self):
        """ The egy is already duplicated if:
            - the academic year is the N+6
        """
        return self.queryset.filter(
            Q(last_year__gte=self.last_academic_year.year) | Q(last_year__gte=F('end_year'))
        )

    def get_to_not_duplicated(self):
        """ We cannot postpone an education_group in the past """
        return self.queryset.filter(last_year__lt=self.current_year.year)

    def post_extend(self):
        """ After the main postponement, we need to create the structure of the education_group_years """
        create_initial_group_element_year_structure(self.result)

    def _extend_objects(self):
        for education_group in self.to_duplicate:
            try:
                with transaction.atomic():
                    last_year = education_group.end_year or self.last_academic_year.year

                    for year in range(education_group.last_year + 1, last_year + 1):
                        new_edy = self.extend_obj(
                            education_group.educationgroupyear_set.latest('academic_year__year'),
                            AcademicYear.objects.get(year=year)
                        )
                        self.result.append(new_edy)

            # General catch to be sure to not stop the rest of the duplication
            except (Error, ObjectDoesNotExist, MultipleObjectsReturned, ConsistencyError):
                self.errors.append(education_group)
