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
import itertools
from typing import List

from django.utils.translation import gettext_lazy as _

from education_group.ddd import command
from education_group.ddd.domain import group, exception, mini_training
from education_group.ddd.repository import mini_training as mini_training_repository, group as group_repository
from education_group.templatetags.academic_year_display import display_as_academic_year


def get_conflicted_fields(cmd: command.GetUpdateMiniTrainingWarningMessages) -> List[str]:
    conflicted_fields = set()
    mini_training_identity = mini_training.MiniTrainingIdentity(acronym=cmd.acronym, year=cmd.year)
    group_identity = group.GroupIdentity(code=cmd.code, year=cmd.year)

    current_mini_training = mini_training_repository.MiniTrainingRepository.get(mini_training_identity)
    current_group = group_repository.GroupRepository.get(group_identity)

    year = cmd.year + 1
    for year in itertools.count(cmd.year+1):
        try:
            next_year_mini_training_identity = mini_training.MiniTrainingIdentity(acronym=cmd.acronym, year=year)
            next_year_mini_training = mini_training_repository.MiniTrainingRepository.get(
                next_year_mini_training_identity
            )

            conflicted_fields.update(
                current_mini_training.get_conflicted_fields(next_year_mini_training)
            )

            next_year_group_identity = group.GroupIdentity(code=cmd.code, year=year)
            next_year_group = group_repository.GroupRepository.get(next_year_group_identity)

            conflicted_fields.update(
                current_group.get_conflicted_fields(next_year_group)
            )
        except exception.MiniTrainingNotFoundException:
            break
        except exception.GroupNotFoundException:
            break
        if conflicted_fields:
            break

        current_mini_training = next_year_mini_training
        current_group = next_year_group

    return [format_warning_message(year, field) for field in conflicted_fields]


def format_warning_message(year: int, field_name: str) -> str:
    return _("Consistency error in %(academic_year)s: %(field)s has already been modified") % {
        "academic_year": display_as_academic_year(year),
        "field": map_field_to_label(field_name)
    }


#  FIXME should be moved to a common file with training
def map_field_to_label(field_name: str) -> str:
    _mapping = {
        "credits": _("Credits"),
        "titles": _("Titles"),
        "status": _("Status"),
        "schedule_type": _("Schedule type"),
        "duration": _("Duration"),
        "duration_unit": _("duration unit"),
        "keywords": _("Keywords"),
        "internship_presence": _("Internship"),
        "is_enrollment_enabled": _("Enrollment enabled"),
        "has_online_re_registration": _("Web re-registration"),
        "has_partial_deliberation": _("Partial deliberation"),
        "has_admission_exam": _("Admission exam"),
        "has_dissertation": _("dissertation"),
        "produce_university_certificate": _("University certificate"),
        "decree_category": _("Decree category"),
        "rate_code": _("Rate code"),
        "main_language": _("Primary language"),
        "english_activities": _("activities in English").capitalize(),
        "other_language_activities": _("Other languages activities"),
        "internal_comment": _("comment (internal)").capitalize(),
        "main_domain": _("main domain"),
        "secondary_domains": _("secondary domains"),
        "isced_domain": _("ISCED domain"),
        "management_entity": _("Management entity"),
        "administration_entity": _("Administration entity"),
        "teaching_campus": _("Learning location"),
        "enrollment_campus": _("Enrollment campus"),
        "other_campus_activities": _("Activities on other campus"),
        "funding": _("Funding"),
        "hops": _("hops"),
        "co_graduation": _("co-graduation"),
        "academic_type": _("Academic type"),
        "diploma": _("Diploma"),
        "content_constraint": _("Content constraint"),
        "remark": _("Remark")
    }
    return _mapping.get(field_name, field_name)
