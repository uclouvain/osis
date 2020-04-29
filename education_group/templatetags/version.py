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
from operator import attrgetter

from django import template
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.program_tree_version import ProgramTreeVersion

register = template.Library()

IDENTIFICATION_URL_NAME = 'education_group_read'
CONTENT_URL_NAME = 'education_group_content'
UTILIZATION_URL_NAME = 'education_group_utilization'


@register.inclusion_tag('education_group/blocks/dropdown/versions.html')
def dropdown_versions(all_versions_available, current_tree_version: ProgramTreeVersion, tab_to_show: str):
    options = []
    ordered_versions_available = _ordered_version_list(all_versions_available)

    for a_version in ordered_versions_available:
        url_computed = _get_version_url_with_tab_to_show(
            a_version.root_group.academic_year.year,
            a_version.root_group.partial_acronym,
            tab_to_show,
        )
        is_current = a_version.version_name == current_tree_version.version_name and \
            a_version.is_transition == current_tree_version.is_transition

        options.append({
            'text': version_label(a_version),
            'selected': is_current,
            'value': url_computed
        })
    return {'options': options}


@register.inclusion_tag('education_group/blocks/dropdown/versions.html')
def dropdown_academic_years(current_tree_version: ProgramTreeVersion, academic_years, tab_to_show: str):
    options = []
    for version_by_year in academic_years:
        url_computed = _get_version_url_with_tab_to_show(
            version_by_year.academic_year.year,
            version_by_year.root_group.partial_acronym,
            tab_to_show,
        )
        options.append({
            'text': version_by_year.academic_year.year,
            'selected': current_tree_version.root_group == version_by_year.root_group,
            'value': url_computed
        })
    return {'options': options}


def _get_version_url_with_tab_to_show(year, code, tab_to_show):
    if tab_to_show == "show_content":
        basic_url = CONTENT_URL_NAME
    elif tab_to_show == 'show_utilization':
        basic_url = UTILIZATION_URL_NAME
    else:
        basic_url = IDENTIFICATION_URL_NAME
    return reverse(basic_url, kwargs={'year': year, 'code': code})


@register.filter
def version_label(a_version):
    return _('Standard') if a_version.version_name == '' and not a_version.is_transition else a_version.version_label


def _ordered_version_list(version_list):
    # List has to be ordered like this
    # Standard version first
    # Transition version second
    # and the particular versions ordered by version_label
    standard_vers = []
    particular_vers = []

    for version in version_list:
        if version.is_standard:
            standard_vers.append(version)
        else:
            particular_vers.append(version)

    return sorted(standard_vers, key=attrgetter("version_label")) + sorted(particular_vers,
                                                                           key=attrgetter("version_label"))
