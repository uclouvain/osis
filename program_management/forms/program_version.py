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
from django import forms
from django.urls import reverse

IDENTIFICATION_URL_NAME = 'education_group_read'
CONTENT_URL_NAME = 'education_group_content'
UTILIZATION_URL_NAME = 'education_group_utilization'


class ProgramVersionForm(forms.Form):

    version_name = None

    version_list_for_url = None     # list of versions to display in dropdown list
    additional_title = None         # complement following the OF acronym if it's a particular version
    displayed_version = None        # current version displayed in screen
    url_identification_tab = None   # url for identification tab
    url_content_tab = None          # url for content tab
    url_utilization_tab = None      # url for utilization tab
    is_particular = False           # used to define css for unversioned field

    def __init__(self, *args, **kwargs):
        self.version_name = kwargs.pop('version_name')
        self.transition = kwargs.pop('transition')
        self.version_view = kwargs.pop('list_of_versions')
        tab_to_show = kwargs.pop('tab_to_show')
        self.version_list_for_url = []

        self.version_list = _ordered_list(self.version_view)

        for a_version in self.version_list:
            is_current = self.is_current(a_version)
            self.version_list_for_url.append({
                'url_identification': _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME,
                                                                                     a_version),
                'url_content': _compute_url_used_in_dropdown_list_of_versions(CONTENT_URL_NAME, a_version),
                'url_utilization': _compute_url_used_in_dropdown_list_of_versions(UTILIZATION_URL_NAME, a_version),
                'version_name': '-' if a_version.version_name == '' else a_version.version_name,
                'version_label': 'Standard' if a_version.version_label == '' else a_version.version_label,
                'selected': 'selected' if is_current else '',
                'url_to_go_to': _get_version_url_with_tab_to_show(a_version, tab_to_show, a_version.offer_id)
            })

            if is_current:
                self.url_identification_tab = _compute_url_used_in_dropdown_list_of_versions(IDENTIFICATION_URL_NAME,
                                                                                             a_version)
                self.url_content_tab = _compute_url_used_in_dropdown_list_of_versions(CONTENT_URL_NAME, a_version)
                self.url_utilization_tab = _compute_url_used_in_dropdown_list_of_versions(UTILIZATION_URL_NAME,
                                                                                          a_version)
                if a_version.is_transition and a_version.version_name == '':
                    self.additional_title = 'Transition'
                else:
                    self.additional_title = a_version.version_label

        super().__init__(*args, **kwargs)

    def is_current(self, a_version):
        is_current = a_version.version_name == self.version_name and a_version.is_transition == self.transition
        if is_current:
            self.displayed_version = a_version
            if a_version.version_name or a_version.is_transition:
                self.is_particular = True
        return is_current


def _ordered_list(version_list):
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


def _get_version_url_with_tab_to_show(a_version, tab_to_show, offer_id):
    if tab_to_show == "show_content":
        basic_url = CONTENT_URL_NAME
    elif tab_to_show == 'show_utilization':
        basic_url = UTILIZATION_URL_NAME
    else:
        basic_url = IDENTIFICATION_URL_NAME

    kwargs = {'education_group_year_id': offer_id}
    url_name = basic_url
    if a_version.is_transition:
        url_name = '{}_transition'.format(basic_url)

    if a_version.version_name:
        kwargs.update({'version_name': a_version.version_name})

    return reverse(url_name, kwargs=kwargs)


def _compute_url_used_in_dropdown_list_of_versions(basic_url, a_version):
    kwargs = {'education_group_year_id': a_version.offer_id}
    url_name = basic_url
    if a_version.is_transition:
        url_name = '{}_transition'.format(basic_url)

    if a_version.version_name:
        kwargs.update({'version_name': a_version.version_name})

    return reverse(url_name, kwargs=kwargs)
