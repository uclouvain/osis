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
import collections
import itertools

from django.utils.translation import gettext_lazy as _

from base.forms.search.search_form import get_research_criteria
from base.views.common import remove_from_session

SIMPLE_SEARCH = 1
SERVICE_COURSES_SEARCH = 2
PROPOSAL_SEARCH = 3
SUMMARY_LIST = 4
BORROWED_COURSE = 5
EXTERNAL_SEARCH = 6

ACTION_BACK_TO_INITIAL = "back_to_initial"
ACTION_CONSOLIDATE = "consolidate"
ACTION_FORCE_STATE = "force_state"

ITEMS_PER_PAGES = 2000


def _manage_session_variables(request, search_type):
    remove_from_session(request, 'search_url')
    if search_type == 'EXTERNAL':
        request.session['ue_search_type'] = str(_('External learning units'))
    elif search_type == SIMPLE_SEARCH:
        request.session['ue_search_type'] = None
    else:
        request.session['ue_search_type'] = str(_get_search_type_label(search_type))


def _get_filter(form, search_type):
    criterias = itertools.chain([(_('Search type'), _get_search_type_label(search_type))], get_research_criteria(form))
    return collections.OrderedDict(criterias)


def _get_search_type_label(search_type):
    return {
        PROPOSAL_SEARCH: _('Proposals'),
        SERVICE_COURSES_SEARCH: _('Service courses'),
        BORROWED_COURSE: _('Borrowed courses')
    }.get(search_type, _('Learning units'))
