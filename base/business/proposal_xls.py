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

from django.utils.translation import ugettext_lazy as _

from osis_common.document import xls_build
from base.business.learning_unit import get_entity_acronym
from base.business.xls import get_name_or_username
from base.models.proposal_learning_unit import find_by_learning_unit_year
from base.models.enums.learning_unit_year_periodicity import PERIODICITY_TYPES

WORKSHEET_TITLE = _('Proposals')
XLS_FILENAME = _('Proposals')
XLS_DESCRIPTION = _("List_proposals")

PROPOSAL_TITLES = [str(_('Req. Entity')), str(_('Code')), str(_('Title')), str(_('Type')),
                   str(_('Proposal type')), str(_('Proposal status')), str(_('Folder num.')),
                   str(_('Decision')), str(_('Periodicity')), str(_('Credits')),
                   str(_('Alloc. Ent.')), str(_('Proposals date'))]


def prepare_xls_content(proposals):
    return [extract_xls_data_from_proposal(proposal) for proposal in proposals]


def extract_xls_data_from_proposal(luy):
    proposal = find_by_learning_unit_year(luy)
    return [luy.entity_requirement.acronym,
            luy.acronym,
            luy.complete_title,
            luy.learning_container_year.get_container_type_display(),
            proposal.get_type_display(),
            proposal.get_state_display(),
            proposal.folder,
            luy.learning_container_year.get_type_declaration_vacant_display(),
            dict(PERIODICITY_TYPES)[luy.periodicity],
            luy.credits,
            luy.entity_allocation.acronym,
            proposal.date.strftime('%d-%m-%Y')]


def prepare_xls_parameters_list(user, working_sheets_data):
    return {xls_build.LIST_DESCRIPTION_KEY: _(XLS_DESCRIPTION),
            xls_build.FILENAME_KEY: _(XLS_FILENAME),
            xls_build.USER_KEY: get_name_or_username(user),
            xls_build.WORKSHEETS_DATA:
                [{xls_build.CONTENT_KEY: working_sheets_data,
                  xls_build.HEADER_TITLES_KEY: PROPOSAL_TITLES,
                  xls_build.WORKSHEET_TITLE_KEY: _(WORKSHEET_TITLE),
                  }
                 ]}


def create_xls(user, proposals, filters):
    ws_data = xls_build.prepare_xls_parameters_list(prepare_xls_content(proposals), configure_parameters(user))
    return xls_build.generate_xls(ws_data, filters)


def configure_parameters(user):
    return {xls_build.DESCRIPTION: XLS_DESCRIPTION,
            xls_build.USER: get_name_or_username(user),
            xls_build.FILENAME: XLS_FILENAME,
            xls_build.HEADER_TITLES: PROPOSAL_TITLES,
            xls_build.WS_TITLE: WORKSHEET_TITLE}
