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
import functools
from decimal import Decimal
from typing import List, Dict, Callable, Any, Tuple

from django.contrib.messages import ERROR, SUCCESS
from django.contrib.messages import INFO
from django.db import IntegrityError
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from base import models as mdl_base
from base.business import learning_unit_year_with_context
from base.business.learning_unit import compose_components_dict
from base.business.learning_unit_year_with_context import volume_from_initial_learning_component_year
from base.business.learning_units.edition import edit_learning_unit_end_date, update_learning_unit_year_with_report, \
    update_partim_acronym
from base.business.learning_units.simple import deletion as business_deletion
from base.models import campus, proposal_learning_unit, person
from base.models.academic_year import find_academic_year_by_year, AcademicYear
from base.models.entity import find_by_id, get_by_internal_id
from base.models.enums import entity_container_year_link_type
from base.models.enums import organization_type
from base.models.enums import proposal_state, proposal_type
from base.models.enums import vacant_declaration_type, attribution_procedure
from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.learning_unit_year_periodicity import PERIODICITY_TYPES
from base.models.enums.proposal_type import ProposalType
from base.utils import send_mail as send_mail_util
from osis_role.errors import get_permission_error
from reference.models import language

BOOLEAN_FIELDS = ('professional_integration', 'is_vacant', 'team')
FOREIGN_KEY_NAME = (
    'language', 'campus', 'requirement_entity', 'allocation_entity', 'additional_entity_1', 'additional_entity_2',
)

END_FOREIGN_KEY_NAME = "_id"
NO_PREVIOUS_VALUE = '-'
# TODO : VALUES_WHICH_NEED_TRANSLATION ?
VALUES_WHICH_NEED_TRANSLATION = ["container_type", "internship_subtype"]
LABEL_ACTIVE = _('Active')
LABEL_INACTIVE = _('Inactive')
INITIAL_DATA_FIELDS = {
    'learning_container_year': [
        "id", "acronym", "common_title", "container_type", "in_charge", "common_title_english", "team", "is_vacant",
        "type_declaration_vacant",
        'requirement_entity', 'allocation_entity', 'additional_entity_1', 'additional_entity_2',
    ],
    'learning_unit': [
        "id", "end_year",
    ],
    'learning_unit_year': [
        "id", "acronym", "specific_title", "internship_subtype", "credits", "campus", "language", "periodicity",
        "status", "professional_integration", "specific_title", "specific_title_english", "quadrimester", "session",
        "attribution_procedure", "faculty_remark", "other_remark", "other_remark_english"
    ],
    'learning_component_year': [
        "id", "acronym", "hourly_volume_total_annual", "hourly_volume_partial_q1", "hourly_volume_partial_q2",
        "planned_classes", "type", "repartition_volume_requirement_entity", "repartition_volume_additional_entity_1",
        "repartition_volume_additional_entity_2"
    ],
}


def compute_proposal_type(proposal_learning_unit_year, learning_unit_year):
    if proposal_learning_unit_year.type in [ProposalType.CREATION.name, ProposalType.SUPPRESSION.name]:
        return proposal_learning_unit_year.type
    differences = get_difference_of_proposal(proposal_learning_unit_year, learning_unit_year)
    differences.pop('components_initial_data', None)
    if differences.get('acronym') and len(differences) == 1:
        return ProposalType.TRANSFORMATION.name
    elif differences.get('acronym'):
        return ProposalType.TRANSFORMATION_AND_MODIFICATION.name
    else:
        return ProposalType.MODIFICATION.name


def reinitialize_data_before_proposal(learning_unit_proposal):
    learning_unit_year = learning_unit_proposal.learning_unit_year
    initial_data = learning_unit_proposal.initial_data
    _reinitialize_model_before_proposal(learning_unit_year, initial_data["learning_unit_year"])
    _reinitialize_model_before_proposal(learning_unit_year.learning_unit, initial_data["learning_unit"])
    _reinitialize_model_before_proposal(learning_unit_year.learning_container_year,
                                        initial_data["learning_container_year"])
    _reinitialize_components_before_proposal(initial_data.get("learning_component_years") or {})


def _reinitialize_model_before_proposal(obj_model, attribute_initial_values):
    for attribute_name, attribute_value in attribute_initial_values.items():
        if attribute_name != "id" and attribute_name != "in_charge":
            cleaned_initial_value = clean_attribute_initial_value(attribute_name, attribute_value)
            setattr(obj_model, attribute_name, cleaned_initial_value)
    obj_model.save()


def clean_attribute_initial_value(attribute_name, attribute_value):
    # TODO : clean this function ; it could make up to 6 hits DB
    clean_attribute_value = attribute_value
    if attribute_name == "campus":
        clean_attribute_value = campus.find_by_id(attribute_value)
    elif attribute_name == "language":
        clean_attribute_value = language.find_by_id(attribute_value)
    elif attribute_name in ['requirement_entity', 'allocation_entity', 'additional_entity_1', 'additional_entity_2']:
        clean_attribute_value = get_by_internal_id(attribute_value)
    elif attribute_name == "end_year" and attribute_value:
        clean_attribute_value = AcademicYear.objects.get(pk=attribute_value)
    return clean_attribute_value


def delete_learning_unit_proposal(learning_unit_proposal, delete_learning_unit):
    lu = learning_unit_proposal.learning_unit_year.learning_unit
    learning_unit_proposal.delete()
    if delete_learning_unit:
        lu.delete()


def get_difference_of_proposal(proposal, learning_unit_year):
    initial_data = proposal.initial_data
    actual_data = copy_learning_unit_data(learning_unit_year)
    differences = {}
    for model in ['learning_unit', 'learning_unit_year', 'learning_container_year', 'entities']:
        initial_data_by_model = initial_data.get(model)
        if not initial_data_by_model:
            continue
        differences = _get_model_differences(actual_data, differences, initial_data_by_model, model)
    return _get_differences_of_proposal_components(differences, proposal)


def _get_the_old_value(key, current_data, initial_data):
    initial_value = initial_data.get(key) or NO_PREVIOUS_VALUE

    if _is_foreign_key(key, current_data):
        return _get_str_representing_old_data_from_foreign_key(key, initial_value)
    else:
        return _get_old_value_when_not_foreign_key(initial_value, key)


def _get_str_representing_old_data_from_foreign_key(key, initial_value):
    if initial_value != NO_PREVIOUS_VALUE:
        return _get_old_value_of_foreign_key(key, initial_value)
    else:
        return NO_PREVIOUS_VALUE


def _get_old_value_of_foreign_key(key, initial_value):
    if key == 'campus':
        return _get_name_attribute(mdl_base.campus.find_by_id(initial_value))

    if key == 'language':
        return _get_name_attribute(language.find_by_id(initial_value))

    return _get_special_old_value(key, initial_value)


def _is_foreign_key(key, current_data):
    return "{}{}".format(key, END_FOREIGN_KEY_NAME) in current_data or '_ENTITY' in key or key in FOREIGN_KEY_NAME


def _get_status_initial_value(initial_value):
    return LABEL_ACTIVE if initial_value else LABEL_INACTIVE


def _get_old_value_when_not_foreign_key(initial_value, key):
    old_value = NO_PREVIOUS_VALUE
    if initial_value != NO_PREVIOUS_VALUE:
        if key in VALUES_WHICH_NEED_TRANSLATION:
            old_value = _(initial_value)
        elif key == 'status':
            old_value = _get_status_initial_value(initial_value)
        elif key in ('periodicity', 'attribution_procedure', 'type_declaration_vacant'):
            old_value = _get_enum_value(key, initial_value)
        elif key in BOOLEAN_FIELDS:
            old_value = "{}".format(_('Yes') if bool(initial_value) else _('No'))
        else:
            old_value = "{}".format(initial_value)
    else:
        if key in BOOLEAN_FIELDS:
            old_value = _('No')

    return old_value


def force_state_of_proposals(proposals, author, new_state):
    change_state = functools.partial(modify_proposal_state, new_state)
    return _apply_action_on_proposals_and_send_report(
        proposals,
        author,
        change_state,
        _("successfully changed state"),
        _("cannot be changed state"),
        None,
        None,
        can_edit_proposal
    )


def can_edit_proposal(proposal, author, raise_exception):
    perm = 'base.can_edit_learning_unit_proposal'
    return perm, author.user.has_perm(perm, proposal.learning_unit_year)


def modify_proposal_state(new_state, proposal):
    proposal.state = new_state
    proposal.save()
    return {}


def cancel_proposals_and_send_report(proposals, author, research_criteria):
    return _apply_action_on_proposals_and_send_report(
        proposals,
        author,
        cancel_proposal,
        _("successfully canceled"),
        _("cannot be canceled"),
        send_mail_util.send_mail_cancellation_learning_unit_proposals,
        research_criteria,
        can_cancel_proposal
    )


def can_cancel_proposal(proposal, author, raise_exception):
    perm = 'base.can_cancel_proposal'
    return perm, author.user.has_perm(perm, proposal.learning_unit_year)


def consolidate_proposals_and_send_report(
        proposals: List[proposal_learning_unit.ProposalLearningUnit],
        author: person.Person,
        research_criteria: Dict) -> Dict[str, List[str]]:
    return _apply_action_on_proposals_and_send_report(
        proposals,
        author,
        consolidate_proposal,
        _('successfully consolidated'),
        _('cannot be consolidated'),
        send_mail_util.send_mail_consolidation_learning_unit_proposal,
        research_criteria,
        can_consolidate_learningunit_proposal
    )


def can_consolidate_learningunit_proposal(proposal, author, raise_exception):
    perm = 'base.can_consolidate_learningunit_proposal'
    return perm, author.user.has_perm(perm, proposal.learning_unit_year)


def _apply_action_on_proposals_and_send_report(
        proposals: List[proposal_learning_unit.ProposalLearningUnit],
        author: person.Person,
        action_method: Callable,
        success_msg_id: str,
        error_msg_id: str,
        send_mail_method: Callable[[person.Person, Any, Dict], None],
        research_criteria: Dict,
        permission_check: Callable) -> Dict[str, List[str]]:
    messages_by_level = {SUCCESS: [], ERROR: []}
    proposals_with_results = _apply_action_on_proposals(proposals, action_method, author, permission_check)

    if send_mail_method:
        send_mail_method(author, proposals_with_results, research_criteria)
        messages_by_level[INFO] = [_("A report has been sent.")]

    for proposal, results in proposals_with_results:
        if ERROR in results:
            messages_by_level[ERROR].append("%(proposal)s %(acronym)s (%(academic_year)s) %(msg_detail)s." % {
                "proposal": _('Proposal'),
                "acronym": proposal.learning_unit_year.acronym,
                "academic_year": proposal.learning_unit_year.academic_year,
                "msg_detail": error_msg_id
            })
        else:
            messages_by_level[SUCCESS].append("%(proposal)s %(acronym)s (%(academic_year)s) %(msg_detail)s." % {
                "proposal": _('Proposal'),
                "acronym": proposal.learning_unit_year.acronym,
                "academic_year": proposal.learning_unit_year.academic_year,
                "msg_detail": success_msg_id
            })
    return messages_by_level


def _apply_action_on_proposals(
        proposals: List[proposal_learning_unit.ProposalLearningUnit],
        action_method: Callable,
        author: person.Person,
        permission_check: Callable[[proposal_learning_unit.ProposalLearningUnit, person.Person, bool], bool]
) -> List[Tuple[proposal_learning_unit.ProposalLearningUnit, Dict]]:
    proposals_with_results = []
    for proposal in proposals:
        perm, perm_result = permission_check(proposal, author, True)
        if perm_result:
            proposal_with_result = (proposal, action_method(proposal))
        else:
            perm_denied_msg = get_permission_error(author.user, perm)
            proposal_with_result = (proposal, {ERROR: _(str(perm_denied_msg))})
        proposals_with_results.append(proposal_with_result)
    return proposals_with_results


def cancel_proposal(proposal):
    results = {}
    if proposal.type == ProposalType.CREATION.name:
        learning_unit_year = proposal.learning_unit_year

        errors = list(business_deletion.check_can_delete_ignoring_proposal_validation(learning_unit_year).values())

        if errors:
            results = {ERROR: errors}
        else:
            results = {SUCCESS: business_deletion.delete_from_given_learning_unit_year(learning_unit_year)}
            delete_learning_unit_proposal(proposal, True)
    else:
        reinitialize_data_before_proposal(proposal)
        delete_learning_unit_proposal(proposal, False)

    return results


def consolidate_proposal(proposal: proposal_learning_unit.ProposalLearningUnit) -> Dict[str, List[str]]:
    results = {ERROR: [_("Proposal is neither accepted nor refused.")]}
    if proposal.state == proposal_state.ProposalState.REFUSED.name:
        results = cancel_proposal(proposal)
    elif proposal.state == proposal_state.ProposalState.ACCEPTED.name:
        results = _consolidate_accepted_proposal(proposal)
        if not results.get(ERROR):
            delete_learning_unit_proposal(proposal, False)
    return results


def _consolidate_accepted_proposal(proposal: proposal_learning_unit.ProposalLearningUnit) -> Dict[str, List[str]]:
    if proposal.type == proposal_type.ProposalType.CREATION.name:
        return _consolidate_creation_proposal_accepted(proposal)
    elif proposal.type == proposal_type.ProposalType.SUPPRESSION.name:
        return _consolidate_suppression_proposal_accepted(proposal)
    return _consolidate_modification_proposal_accepted(proposal)


def _consolidate_creation_proposal_accepted(proposal):
    proposal.learning_unit_year.learning_unit.end_year = proposal.learning_unit_year.academic_year

    results = {SUCCESS: edit_learning_unit_end_date(proposal.learning_unit_year.learning_unit, None)}
    return results


def _consolidate_suppression_proposal_accepted(proposal):
    initial_end_year = proposal.initial_data["learning_unit"]["end_year"]
    new_end_year = proposal.learning_unit_year.learning_unit.end_year

    proposal.learning_unit_year.learning_unit.end_year = find_academic_year_by_year(initial_end_year)
    try:
        results = {SUCCESS: edit_learning_unit_end_date(proposal.learning_unit_year.learning_unit, new_end_year)}
    except IntegrityError as err:
        results = {ERROR: err.args[0]}
    return results


def _consolidate_modification_proposal_accepted(proposal: proposal_learning_unit.ProposalLearningUnit) -> Dict:
    update_partim_acronym(proposal.learning_unit_year.acronym, proposal.learning_unit_year)
    next_luy = proposal.learning_unit_year.get_learning_unit_next_year()
    if next_luy:
        fields_to_update = {}
        fields_to_update.update(model_to_dict(proposal.learning_unit_year,
                                              fields=proposal.initial_data["learning_unit_year"].keys(),
                                              exclude=("id",)))
        fields_to_update.update(model_to_dict(proposal.learning_unit_year.learning_unit,
                                              fields=proposal.initial_data["learning_unit"].keys(),
                                              exclude=("id",)))
        fields_to_update.update(model_to_dict(proposal.learning_unit_year.learning_container_year,
                                              fields=proposal.initial_data["learning_container_year"].keys(),
                                              exclude=("id",)))
        fields_to_update_clean = {}
        for field_name, field_value in fields_to_update.items():
            fields_to_update_clean[field_name] = clean_attribute_initial_value(field_name, field_value)

        entities_to_update = proposal.learning_unit_year.learning_container_year.get_map_entity_by_type()

        update_learning_unit_year_with_report(next_luy, fields_to_update_clean, entities_to_update,
                                              override_postponement_consistency=True,
                                              lu_to_consolidate=proposal.learning_unit_year)
    return {}


def compute_proposal_state(a_person):
    return proposal_state.ProposalState.CENTRAL.name if a_person.is_central_manager \
        else proposal_state.ProposalState.FACULTY.name


def copy_learning_unit_data(learning_unit_year):
    learning_container_year = learning_unit_year.learning_container_year
    entities_by_type = learning_container_year.get_map_entity_by_type()

    learning_unit_year_values = _get_attributes_values(learning_unit_year,
                                                       INITIAL_DATA_FIELDS['learning_unit_year'])
    learning_unit_year_values["credits"] = learning_unit_year.credits if learning_unit_year.credits else None

    return {
        "learning_container_year": _get_attributes_values(learning_container_year,
                                                          INITIAL_DATA_FIELDS['learning_container_year']),
        "learning_unit_year": learning_unit_year_values,
        "learning_unit": _get_attributes_values(learning_unit_year.learning_unit,
                                                INITIAL_DATA_FIELDS['learning_unit']),
        # TODO :: remove "entities" key, duplicated with entities in LearningContainerYear
        "entities": get_entities(entities_by_type),
        "learning_component_years": get_components_initial_data(learning_unit_year),
        "volumes": _get_volumes_for_initial(learning_unit_year)
    }


def _get_attributes_values(obj, attributes_name):
    return model_to_dict(obj, fields=attributes_name)


def get_entities(entities_by_type):
    return {entity_type: get_entity_by_type(entity_type, entities_by_type) for entity_type in ENTITY_TYPE_LIST}


def get_entity_by_type(entity_type, entities_by_type):
    if entities_by_type.get(entity_type):
        return entities_by_type[entity_type].id
    else:
        return None


def update_or_create_learning_unit_component(obj_model, attribute_initial_values):
    for attribute_name, attribute_value in attribute_initial_values.items():
        if attribute_name != "id":
            cleaned_initial_value = clean_attribute_initial_value(attribute_name, attribute_value)
            setattr(obj_model, attribute_name, cleaned_initial_value)
    obj_model.save()


def _reinitialize_components_before_proposal(initial_components):
    for initial_data_by_model in initial_components:
        an_id = initial_data_by_model.get('id')
        if an_id:
            learning_component_year = mdl_base.learning_component_year.LearningComponentYear.objects.get(pk=an_id)
            update_or_create_learning_unit_component(learning_component_year, initial_data_by_model)


def get_components_initial_data(learning_unit_year):
    components = mdl_base.learning_component_year.find_by_learning_container_year(
        learning_unit_year.learning_container_year)
    component_values_list = []
    for component in components:
        data = _get_attributes_values(component, INITIAL_DATA_FIELDS['learning_component_year'])
        component_values_list.append(data)
    return component_values_list


def get_components_identification_initial_data(proposal):
    components = []
    additional_entities = proposal.initial_data.get('entities')
    learning_component_year_list_from_initial = proposal.initial_data.get('learning_component_years')
    if learning_component_year_list_from_initial:
        for learning_component_year in learning_component_year_list_from_initial:
            components.append(
                {
                    'learning_component_year': learning_component_year,
                    'volumes': volume_from_initial_learning_component_year(
                        learning_component_year,
                        proposal.initial_data.get('volumes')[learning_component_year['acronym']]
                    )
                }
            )
        return compose_components_dict(components, additional_entities)
    return None


def _get_enum_value(key, a_enum_value):
    if key == 'periodicity':
        return _get_value_from_enum(PERIODICITY_TYPES, a_enum_value)
    elif key == 'attribution_procedure':
        return _get_value_from_enum(attribution_procedure.ATTRIBUTION_PROCEDURES, a_enum_value)
    elif key == 'type_declaration_vacant':
        return _get_value_from_enum(vacant_declaration_type.DECLARATION_TYPE, a_enum_value)
    else:
        return None


def _get_value_from_enum(tup, enum_value):
    return dict(tup)[enum_value] if enum_value else NO_PREVIOUS_VALUE


def _get_differences_of_proposal_components(differences_param, proposal):
    differences = differences_param
    comp = get_components_identification_initial_data(proposal)
    if comp:
        differences['components_initial_data'] = get_components_identification_initial_data(proposal)
    return differences


def _get_name_attribute(obj):
    return obj.name if obj else None


def _get_model_differences(actual_data, differences_param, initial_data_by_model, model):
    differences = differences_param
    for column_name, value in initial_data_by_model.items():
        if value is not None and column_name == 'credits':
            value = Decimal(value)
        if not (value is None and actual_data[model][column_name] == '') and value != actual_data[model][column_name]:
            differences[column_name] = _get_the_old_value(column_name, actual_data[model], initial_data_by_model)
    return differences


def _get_volumes_for_initial(learning_unit_year):
    # Add volumes dict to initial_data by type
    volumes = None
    learning_unit_yrs = learning_unit_year_with_context.get_with_context(
        learning_container_year_id=learning_unit_year.learning_container_year.id)

    volumes = next(luy.components for luy in learning_unit_yrs if luy.id == learning_unit_year.id)

    volumes_for_initial = {}
    for component_key, volume_data in volumes.items():
        volumes_for_initial[component_key.acronym] = volume_data

    return volumes_for_initial


def _get_special_old_value(key, initial_value):
    if key in (entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1,
               entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2):
        an_entity = find_by_id(initial_value)
        if an_entity.organization.type != organization_type.MAIN:
            return an_entity.most_recent_entity_version.title if an_entity else None
        else:
            return an_entity.most_recent_acronym if an_entity else None
    elif '_ENTITY' in key:
        an_entity = find_by_id(initial_value)
        return an_entity.most_recent_acronym if an_entity else None

    return None
