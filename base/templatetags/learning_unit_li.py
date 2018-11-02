#############################################################################
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
from django import template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied

from base.models.person import find_by_user
from base.business.learning_units.perms import is_year_editable, YEAR_LIMIT_LUE_MODIFICATION
from base.business.learning_units.perms import is_eligible_for_modification, is_eligible_for_modification_end_date, \
    is_eligible_to_create_modification_proposal, is_eligible_to_edit_proposal, is_eligible_for_cancel_of_proposal, \
    is_eligible_to_consolidate_proposal,is_eligible_to_delete_learning_unit_year

register = template.Library()

MSG_IS_NOT_A_PROPOSAL = "Isn't a proposal"
MSG_PROPOSAL_NOT_ON_CURRENT_LU = "Proposal isn't on current learning unit year"
DISABLED = "disabled"


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_edit_lu(context, url, message, url_id="link_edit_lu"):
    return li_with_permission(context, is_eligible_for_modification, url, message, url_id, False)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_edit_date_lu(context, url, message, url_id="link_edit_date_lu"):
    return li_with_permission(context, is_eligible_for_modification_end_date, url, message, url_id, False)


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_suppression_proposal(context, url, message, url_id="link_proposal_suppression", js_script=''):
    return li_with_permission_for_proposal(context, is_eligible_to_create_modification_proposal, url, message, url_id, True,js_script, context['learning_unit_year'])


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_modification_proposal(context, url, message, url_id="link_proposal_modification", js_script=''):
    return li_with_permission_for_proposal(context, is_eligible_to_create_modification_proposal, url, message, url_id, False, js_script, context['learning_unit_year'])


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_edit_proposal(context, url, message, url_id="link_proposal_edit", js_script=''):
    return li_with_permission_for_proposal(context, is_eligible_to_edit_proposal, url, message, url_id, False, js_script, context['proposal'])


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_cancel_proposal(context, url, message, url_id="link_cancel_proposal", js_script=''):
    return li_with_permission_for_proposal(context, is_eligible_for_cancel_of_proposal, url, message, url_id, False, js_script, context['proposal'])


@register.inclusion_tag('blocks/button/li_template.html', takes_context=True)
def li_consolidate_proposal(context, url, message, url_id="link_consolidate_proposal", js_script=''):
    return li_with_permission_for_proposal(context, is_eligible_to_consolidate_proposal, url, message, url_id, False, js_script, context['proposal'])


@register.inclusion_tag('blocks/button/li_template_lu.html', takes_context=True)
def li_delete_all_lu(context, url, message, data_target, url_id="link_delete_lus"):
    data = li_with_permission(context, is_eligible_to_delete_learning_unit_year, url, message, url_id, True, data_target)

    return data


def li_with_permission(context, permission, url, message, url_id, load_modal=False, data_target=''):
    permission_denied_message, disabled = _get_permission(context, permission)

    if not disabled:
        href = url
    else:
        href = "#"
        load_modal = False
        data_target=''

    return {
        "class_li": disabled,
        "load_modal": load_modal,
        "url": href,
        "id_li": url_id,
        "title": permission_denied_message,
        "text": message,
        "data_target": data_target
    }


def _get_permission(context, permission):
    permission_denied_message = ""
    learning_unit_year = context.get('learning_unit_year')
    person = find_by_user(context.get('user'))
    try:
        result = permission(learning_unit_year, person, raise_exception=True)
    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    return permission_denied_message, "" if result else "disabled"


def li_with_permission_for_proposal(context, permission, url, message, url_id, load_modal=False, js_script='', obj=None):
    proposal = context['proposal']
    person = find_by_user(context.get('user'))

    permission_denied_message, disabled = is_valid_proposal(context)

    if not disabled:
        if not is_year_editable(proposal.learning_unit_year, person, raise_exception=False):
            disabled = "disabled"
            permission_denied_message = "{}"\
                .format(_("You can't modify proposition which are related to a learning unit year under"))
        else:
            permission_denied_message, disabled = _get_permission_proposal(context, permission , obj)

    if not disabled:
        href = url
    else:
        href = "#"
        load_modal = False

    return {
        "class_li": disabled,
        "load_modal": load_modal,
        "url": href,
        "id_li": url_id,
        "title": permission_denied_message,
        "text": message,
        "js_script": js_script,
    }


def _get_permission_proposal(context, permission, proposal):
    permission_denied_message = ""

    person = find_by_user(context.get('user'))
    try:
        # attention ça marche pour certains test avec la ligne ci-dessous et pour d'autre avec la suivante

        result = permission(proposal, person, raise_exception=True)
        # result = permission(proposal.learning_unit_year, person, raise_exception=True)
    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    return permission_denied_message, "" if result else DISABLED


def is_valid_proposal(context):

    current_learning_unit_year = context.get('learning_unit_year')
    proposal = context.get('proposal')
    if not proposal:
        return _(MSG_IS_NOT_A_PROPOSAL), "disabled"
    else:


        if proposal.learning_unit_year != current_learning_unit_year:

            return _(MSG_PROPOSAL_NOT_ON_CURRENT_LU), "disabled"
        # else:
        #     try:
        #         result = permission(learning_unit_year, person, raise_exception=True)
        #     except PermissionDenied as e:
        #         result = False
        #         permission_denied_message = str(e)

    return "" , ""