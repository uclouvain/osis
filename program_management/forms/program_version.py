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

    is_standard = False
    version_name = None

    version_list_for_url = None
    additional_title = None     # complement following the OF acronym if it's a particular version
    displayed_version = None
    url_identification_tab = None
    url_content_tab = None
    url_utilization_tab = None
    is_particular = False

    def __init__(self, *args, **kwargs):
        self.version_name = kwargs.pop('version_name')
        self.transition = kwargs.pop('transition')
        self.version_view = kwargs.pop('list_of_versions')
        self.version_list_for_url = []

        self.version_list = ordered_list(self.version_view)

        for a_version in self.version_list:
            is_current = self.is_current(a_version)
            self.version_list_for_url.append({
                'url_identification': _compute_url(IDENTIFICATION_URL_NAME, a_version, a_version.offer),
                'url_content': _compute_url(CONTENT_URL_NAME, a_version, a_version.offer),
                'url_utilization': _compute_url(UTILIZATION_URL_NAME, a_version, a_version.offer),
                'version_name': '-' if a_version.version_name == '' else a_version.version_name,
                'version_label': 'Standard' if a_version.version_label == '' else a_version.version_label,
                'selected': 'selected' if is_current else ''})

            if is_current:
                self.url_identification_tab = _compute_url(IDENTIFICATION_URL_NAME, a_version, a_version.offer)
                self.url_content_tab = _compute_url(CONTENT_URL_NAME, a_version, a_version.offer)
                self.url_utilization_tab = _compute_url(UTILIZATION_URL_NAME, a_version, a_version.offer)

                if a_version.is_transition and a_version.version_name == '':
                    self.additional_title = 'Transition'
                else:
                    self.additional_title = a_version.version_label

        self.is_standard = self.version_name == ''

        super().__init__(*args, **kwargs)

    def is_current(self, a_version):
        is_current = a_version.version_name == self.version_name and a_version.is_transition == self.transition
        if is_current:
            self.displayed_version = a_version
            if a_version.version_name or a_version.is_transition:
                self.is_particular = True
        return is_current


def ordered_list(version_list):
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


def find_version(current_version_name: str, current_transition: bool, list_of_version):

    for a_version in list_of_version:
        if a_version.version_name == current_version_name:
            is_particular = current_transition and not a_version.is_standard
            is_standard = not current_transition and a_version.is_standard
            if is_particular or is_standard:
                return a_version.version_label
    return None


def _compute_url(basic_url, a_version, offer_id):
    kwargs = {'education_group_year_id': offer_id}
    url_name = basic_url
    if a_version.is_transition:
        url_name = '{}_transition'.format(basic_url)

    if a_version.version_name:
        kwargs.update({'version_name': a_version.version_name})

    return reverse(url_name, kwargs=kwargs)
