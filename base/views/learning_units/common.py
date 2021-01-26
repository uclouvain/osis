##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import re
from typing import Optional, List

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

from base import models as mdl
from base.business.learning_unit import get_organization_from_learning_unit_year, get_all_attributions, \
    get_components_identification
from base.business.learning_unit_proposal import get_difference_of_proposal
from base.business.learning_units.edition import create_learning_unit_year_creation_message
from base.business.learning_units.perms import is_eligible_to_update_learning_unit_pedagogy, \
    is_eligible_to_update_learning_unit_pedagogy_force_majeure_section
from base.models import proposal_learning_unit
from base.models.learning_unit import REGEX_BY_SUBTYPE
from base.models.learning_unit_year import LearningUnitYear
from base.views.common import display_success_messages
from osis_common.decorators.ajax import ajax_required
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.translation import gettext_lazy as _

from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories.node import NodeRepository
from program_management.ddd.service.read.search_program_trees_using_node_service import search_program_trees_using_node
from program_management.serializers.program_trees_utilizations import utilizations_serializer


def show_success_learning_unit_year_creation_message(request, learning_unit_year_created):
    success_msg = create_learning_unit_year_creation_message(learning_unit_year_created)
    display_success_messages(request, success_msg, extra_tags='safe')


@login_required
@ajax_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def check_acronym(request, subtype):
    acronym = request.GET['acronym']
    academic_yr_id = request.GET.get('year_id', None)
    if not academic_yr_id:
        raise HttpResponseNotFound
    academic_yr = mdl.academic_year.find_academic_year_by_id(int(academic_yr_id))
    existed_acronym = False
    existing_acronym = False
    first_using = ""
    last_using = ""
    learning_unit_year = mdl.learning_unit_year.find_gte_year_acronym(academic_yr, acronym).first()
    old_learning_unit_year = mdl.learning_unit_year.find_lt_year_acronym(academic_yr, acronym).last()
    # FIXME there is the same check in the models
    if old_learning_unit_year:
        last_using = str(old_learning_unit_year.academic_year)
        existed_acronym = True

    if learning_unit_year:
        first_using = str(learning_unit_year.academic_year)
        existing_acronym = True

    if subtype not in REGEX_BY_SUBTYPE:
        valid = False
    else:
        valid = bool(re.match(REGEX_BY_SUBTYPE[subtype], acronym))

    return JsonResponse({'valid': valid, 'existing_acronym': existing_acronym, 'existed_acronym': existed_acronym,
                         'first_using': first_using, 'last_using': last_using}, safe=False)


def get_learning_unit_identification_context(learning_unit_year_id, person, messages):
    context = get_common_context_learning_unit_year(person, learning_unit_year_id, messages=messages)

    learning_unit_year = context['learning_unit_year']
    context['warnings'] = learning_unit_year.warnings
    proposal = proposal_learning_unit.find_by_learning_unit(learning_unit_year.learning_unit)

    context["can_create_partim"] = person.user.has_perm('base.can_create_partim', learning_unit_year)
    context['learning_container_year_partims'] = learning_unit_year.get_partims_related()
    context['organization'] = get_organization_from_learning_unit_year(learning_unit_year)
    context['campus'] = learning_unit_year.campus
    context.update(get_all_attributions(learning_unit_year))
    components = get_components_identification(learning_unit_year)
    context['components'] = components.get('components')
    context['REQUIREMENT_ENTITY'] = components.get('REQUIREMENT_ENTITY')
    context['ADDITIONAL_REQUIREMENT_ENTITY_1'] = components.get('ADDITIONAL_REQUIREMENT_ENTITY_1')
    context['ADDITIONAL_REQUIREMENT_ENTITY_2'] = components.get('ADDITIONAL_REQUIREMENT_ENTITY_2')
    context['proposal'] = proposal
    context['proposal_folder_entity_version'] = mdl.entity_version.get_by_entity_and_date(
        proposal.entity, None) if proposal else None
    context['differences'] = get_difference_of_proposal(proposal, learning_unit_year) \
        if proposal and proposal.learning_unit_year == learning_unit_year \
        else {}

    # append permissions
    luy = learning_unit_year
    context.update({
        'can_propose': person.user.has_perm('base.can_propose_learningunit', luy),
        'can_edit_date': person.user.has_perm('base.can_edit_learningunit_date', luy),
        'can_edit': person.user.has_perm('base.can_edit_learningunit', luy),
        'can_delete': person.user.has_perm('base.can_delete_learningunit', luy),
        'can_cancel_proposal': person.user.has_perm('base.can_cancel_proposal', luy),
        'can_edit_learning_unit_proposal': person.user.has_perm('base.can_edit_learning_unit_proposal', luy),
        'can_consolidate_proposal': person.user.has_perm('base.can_consolidate_learningunit_proposal', luy),
        'can_manage_volume': person.user.has_perm('base.can_edit_learningunit', luy),
    })

    return context


def get_common_context_learning_unit_year(person,
                                          learning_unit_year_id: Optional[int] = None,
                                          code: Optional[str] = None,
                                          year: Optional[int] = None,
                                          messages: List = []):
    query_set = LearningUnitYear.objects.all().select_related(
        'learning_unit',
        'learning_container_year'
    ).prefetch_related(
        Prefetch(
            'learning_unit__learningunityear_set',
            queryset=LearningUnitYear.objects.select_related('academic_year')
        )
    )
    if learning_unit_year_id:
        learning_unit_year = get_object_or_404(query_set, pk=learning_unit_year_id)
    else:
        learning_unit_year = query_set.get(acronym=code, academic_year__year=year)
    context = {
        'learning_unit_year': learning_unit_year,
        'current_academic_year': mdl.academic_year.starting_academic_year(),
        'is_person_linked_to_entity': person.is_linked_to_entity_in_charge_of_learning_unit_year(learning_unit_year),
    }

    context['special_warning_messages'] = update_context_with_messages_update_warnings(messages)
    return context


def get_text_label_translated(text_lb, user_language):
    return next((txt for txt in text_lb.translated_text_labels
                 if txt.language == user_language), None)


def get_common_context_to_publish(person, learning_unit_year: LearningUnitYear):
    luy_in_current_or_future_anac = not learning_unit_year.academic_year.is_past
    perm_to_edit = is_eligible_to_update_learning_unit_pedagogy(learning_unit_year, person)
    perm_to_edit_force_majeure = is_eligible_to_update_learning_unit_pedagogy_force_majeure_section(
        learning_unit_year,
        person
    )

    return {
        'enable_publish_button':  (perm_to_edit or perm_to_edit_force_majeure) and luy_in_current_or_future_anac,
        'luy_in_current_or_future_anac': luy_in_current_or_future_anac,
        'can_edit_information': perm_to_edit,
        'can_edit_force_majeur_section': perm_to_edit_force_majeure
    }


def check_formations_impacted_by_update(learning_unit_year: LearningUnitYear, request):
    formations_using_ue = _find_root_trainings_using_ue(learning_unit_year.acronym,
                                                        learning_unit_year.academic_year.year)
    if len(formations_using_ue) > 1:
        for formation in formations_using_ue:
            messages.add_message(request, 50, formation)


def _find_root_trainings_using_ue(acronym: str, year: int) -> List['str']:
    node_identity = NodeIdentity(code=acronym, year=year)
    direct_parents = utilizations_serializer(node_identity, search_program_trees_using_node, NodeRepository())

    parents_root = set()
    for direct_link in direct_parents:
        root = None
        parent_node = direct_link.get('link').parent
        for indirect_parent in direct_link.get('indirect_parents'):
            parent_node = indirect_parent.get('node')
            indirect_parents = indirect_parent.get('indirect_parents')
            if (indirect_parents is None or len(indirect_parents) == 0) or parent_node.is_minor_or_deepening():
                root = indirect_parent.get('node')
                break
            else:
                for indirect_parent_of_indirect_parent in indirect_parents:
                    node = indirect_parent_of_indirect_parent.get('node')
                    if parent_node.is_finality() and node.is_training():
                        root = node
                        break
        if root is None:
            root = parent_node
        parents_root.add(root)

    formations_using_ue = ["{} - {}".format(parent.full_acronym(), parent.full_title())for parent in parents_root]
    return sorted(formations_using_ue)


def update_context_with_messages_update_warnings(all_messages):
    messages_update_warning = [m.message for m in all_messages if m.tags == '']
    if messages_update_warning:
        html = "{}<ul>".format(_('Pay attention! This learning unit is used in more than one formation'))
        for message in messages_update_warning:
            html += "<li>{}</li>".format(message)
        html += "</ul>"
        return mark_safe(html)
    return None
