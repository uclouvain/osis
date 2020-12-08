############################################################################
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
############################################################################
from typing import Optional

from django.db.models import Window
from django.db.models.functions import Lag, Lead
from django.template.defaulttags import register
from django.urls import reverse

from base.forms.learning_unit.search.borrowed import BorrowedLearningUnitSearch
from base.forms.learning_unit.search.educational_information import LearningUnitDescriptionFicheFilter
from base.forms.learning_unit.search.external import ExternalLearningUnitFilter
from base.forms.learning_unit.search.service_course import ServiceCourseFilter
from base.forms.learning_unit.search.simple import LearningUnitFilter
from base.forms.proposal.learning_unit_proposal import ProposalLearningUnitFilter
from base.models.enums.education_group_categories import TRAINING, GROUP, MINI_TRAINING
from base.models.learning_unit_year import LearningUnitYear
from base.utils.cache import SearchParametersCache
from base.utils.db import convert_order_by_strings_to_expressions
from base.views.learning_units.search.common import SearchTypes
from education_group.models.group_year import GroupYear
from program_management.ddd.business_types import *
from program_management.forms.education_groups import GroupFilter


@register.inclusion_tag('templatetags/navigation_learning_unit.html', takes_context=False)
def navigation_learning_unit(user, obj: LearningUnitYear, url_name: str):
    return _navigation_base(_get_learning_unit_filter_class, _reverse_learning_unit_year_url, user, obj, url_name,
                            "acronym", True)


@register.inclusion_tag('templatetags/navigation_education_group.html', takes_context=False)
def navigation_group(user, obj: GroupYear, url_name: str, current_version: Optional['ProgramTreeVersion'] = None):
    return _navigation_base(_get_group_filter_class, _reverse_group_year_url, user, obj, url_name, "partial_acronym",
                            False,
                            current_version)


def _navigation_base(filter_class_function, reverse_url_function, user, obj, url_name, code_field_name, is_ue=False,
                     current_version: Optional['ProgramTreeVersion'] = None):
    context = {"current_element": obj}
    if current_version:
        context.update({'current_version': current_version})
    search_parameters = SearchParametersCache(user, obj.__class__.__name__).cached_data
    if not search_parameters:
        return context

    search_type = search_parameters.get("search_type")
    filter_form_class = filter_class_function(search_type)

    order_by = filter_form_class(data=search_parameters).qs.query.order_by
    order_by_expressions = convert_order_by_strings_to_expressions(order_by) or None

    qs = filter_form_class(data=search_parameters).qs.annotate(
        previous_title=Window(
            expression=Lag("acronym"),
            order_by=order_by_expressions,
        ),
        next_title=Window(
            expression=Lead("acronym"),
            order_by=order_by_expressions,
        ),
        previous_code=Window(
            expression=Lag(code_field_name),
            order_by=order_by_expressions,
        ),
        next_code=Window(
            expression=Lead(code_field_name),
            order_by=order_by_expressions,
        ),
        previous_year=Window(
            expression=Lag("academic_year__year"),
            order_by=order_by_expressions,
        ),
        next_year=Window(
            expression=Lead("academic_year__year"),
            order_by=order_by_expressions,
        ),
        previous_id=Window(
            expression=Lag("id"),
            order_by=order_by_expressions,
        ),
        next_id=Window(
            expression=Lead("id"),
            order_by=order_by_expressions,
        )
    )

    if isinstance(obj, GroupYear):
        qs = qs.annotate(
            previous_category=Window(
                expression=Lag("education_group_type__category"),
                order_by=order_by_expressions,
            ),
            next_category=Window(
                expression=Lead("education_group_type__category"),
                order_by=order_by_expressions,
            ),
            previous_element=Window(
                expression=Lag("element"),
                order_by=order_by_expressions,
            ),
            next_element=Window(
                expression=Lead("element"),
                order_by=order_by_expressions,
            )
        )

        fields_names = [
            "id", "acronym", "previous_code", "previous_id", "previous_year", "previous_category", "previous_element",
            "next_code", "next_id", "next_year", "next_category", "previous_title", "next_title", "next_element"
        ]
    else:
        fields_names = [
            "id", "acronym", "previous_code", "previous_id", "previous_year", "next_code", "next_id", "next_year",
            "previous_title", "next_title"
        ]

    if is_ue:
        qs = qs.values_list(*fields_names, named=True).order_by(*order_by)
    else:
        qs = qs.annotate(
            previous_version_label=Window(
                expression=Lag("educationgroupversion__version_name"),
                order_by=order_by_expressions,
            ),
            next_version_label=Window(
                expression=Lead("educationgroupversion__version_name"),
                order_by=order_by_expressions,
            )
        ).values_list(
            *fields_names,
            'previous_version_label',
            'next_version_label',
            named=True
        ).order_by(*order_by)

    current_row = _get_current_row(qs, obj)

    if current_row:
        if isinstance(obj, GroupYear):
            category = {
                TRAINING: "training_identification",
                GROUP: "group_identification",
                MINI_TRAINING: "mini_training_identification"
            }
            context.update({
                "next_element_title": _get_title(
                    current_row.next_title, current_row.next_version_label if not is_ue else None
                ),
                "next_url": reverse_url_function(
                    current_row.next_code,
                    current_row.next_year,
                    category[current_row.next_category]
                ) + '?path={}'.format(current_row.next_element) if current_row.next_element else None,
                "previous_element_title": _get_title(
                    current_row.previous_title, current_row.previous_version_label if not is_ue else None
                ),
                "previous_url": reverse_url_function(
                    current_row.previous_code, current_row.previous_year, category[current_row.previous_category]
                ) + '?path={}'.format(current_row.previous_element) if current_row.previous_element else None
            })

        else:
            context.update({
                "next_element_title": _get_title(
                    current_row.next_title, current_row.next_version_label if not is_ue else None
                ),
                "next_url": reverse_url_function(current_row.next_code, current_row.next_year, url_name)
                if current_row.next_id else None,
                "previous_element_title": _get_title(
                    current_row.previous_title, current_row.previous_version_label if not is_ue else None
                ),
                "previous_url": reverse_url_function(current_row.previous_code, current_row.previous_year, url_name)
                if current_row.previous_id else None
            })
    return context


def _get_group_filter_class(search_type):
    return GroupFilter


def _get_learning_unit_filter_class(search_type):
    map_search_type_to_filter_form = {
        SearchTypes.SIMPLE_SEARCH.value: LearningUnitFilter,
        SearchTypes.SERVICE_COURSES_SEARCH.value: ServiceCourseFilter,
        SearchTypes.PROPOSAL_SEARCH.value: ProposalLearningUnitFilter,
        SearchTypes.SUMMARY_LIST.value: LearningUnitDescriptionFicheFilter,
        SearchTypes.BORROWED_COURSE.value: BorrowedLearningUnitSearch,
        SearchTypes.EXTERNAL_SEARCH.value: ExternalLearningUnitFilter,
    }
    return map_search_type_to_filter_form.get(int(search_type) if search_type else None, LearningUnitFilter)


def _get_current_row(qs, obj):
    return next((row for row in qs if row.id == obj.id), None)


def _reverse_group_year_url(partial_acronym, year, url_name):
    return reverse(url_name, args=[year, partial_acronym])


def _reverse_learning_unit_year_url(acronym, year, url_name):
    return reverse(url_name, args=[acronym, year])


def _get_title(title, version_label_o):
    if title is None and version_label_o is None:
        return None
    return "{}{}".format(
        title,
        "[{}]".format(version_label_o) if version_label_o else ''
    )
