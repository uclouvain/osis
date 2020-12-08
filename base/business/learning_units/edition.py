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
import logging
from typing import Dict, List, Any

from django.conf import settings
from django.db import IntegrityError, transaction, Error
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base import models as mdl_base
from base.business import learning_unit_year_with_context
from base.business.learning_unit import CMS_LABEL_SUMMARY, CMS_LABEL_PEDAGOGY_FR_AND_EN, \
    CMS_LABEL_PEDAGOGY_FR_ONLY, CMS_LABEL_SPECIFICATIONS
from base.business.learning_unit import get_academic_year_postponement_range
from base.business.learning_units.pedagogy import postpone_teaching_materials
from base.business.learning_units.simple.deletion import delete_from_given_learning_unit_year, \
    check_learning_unit_year_deletion
from base.business.utils.model import update_instance_model_from_data, update_related_object
from base.enums.component_detail import COMPONENT_DETAILS
from base.forms.learning_achievement import update_future_luy as update_future_luy_achievement
from base.forms.learning_unit_specifications import update_future_luy
from base.forms.utils.choice_field import NO_PLANNED_END_DISPLAY
from base.models import academic_year
from base.models.academic_year import AcademicYear, compute_max_academic_year_adjournment
from base.models.entity import Entity
from base.models.enums import learning_unit_year_subtypes, learning_component_year_type
from base.models.enums.component_type import COMPONENT_TYPES
from base.models.enums.entity_container_year_link_type import ENTITY_TYPE_LIST
from base.models.enums.proposal_type import ProposalType
from base.models.learning_achievement import LearningAchievement
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from base.models.proposal_learning_unit import ProposalLearningUnit
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from learning_unit.models.learning_class_year import LearningClassYear
from osis_common.utils.numbers import normalize_fraction
from reference.models.language import Language

logger = logging.getLogger(settings.DEFAULT_LOGGER)
FIELDS_TO_EXCLUDE_WITH_REPORT = ("is_vacant", "type_declaration_vacant", "attribution_procedure")
NO_DATA = _('No data')


# TODO :: Use LearningUnitPostponementForm to extend/shorten a LearningUnit and remove all this code
def edit_learning_unit_end_date(learning_unit_to_edit: LearningUnit,
                                new_academic_year: AcademicYear,
                                propagate_end_date_to_luy=True) -> List:
    result = []
    new_end_year = _get_new_end_year(new_academic_year)

    if propagate_end_date_to_luy:
        result.extend(_update_learning_unit_year_end_date(learning_unit_to_edit, new_academic_year, new_end_year))

    result.append(_update_end_year_field(learning_unit_to_edit, new_end_year))
    return result


def _update_learning_unit_year_end_date(learning_unit_to_edit: LearningUnit,
                                        new_academic_year: AcademicYear,
                                        new_end_year):
    end_year = _get_actual_end_year(learning_unit_to_edit)
    if new_end_year is None or new_end_year.year > end_year.year:
        return extend_learning_unit(learning_unit_to_edit, new_academic_year)
    elif new_end_year.year < end_year.year:
        return shorten_learning_unit(learning_unit_to_edit, new_academic_year)
    return []


# TODO :: Use LearningUnitPostponementForm to extend/shorten a LearningUnit and remove all this code
def shorten_learning_unit(learning_unit_to_edit, new_academic_year):
    _check_shorten_partims(learning_unit_to_edit, new_academic_year)

    learning_unit_year_to_delete = LearningUnitYear.objects.filter(
        learning_unit=learning_unit_to_edit,
        academic_year__year__gte=new_academic_year.year + 1
    ).order_by('academic_year').first()

    if not learning_unit_year_to_delete:
        return []

    warning_msg = check_learning_unit_year_deletion(learning_unit_year_to_delete)
    if warning_msg:
        raise IntegrityError(list(warning_msg.values()))

    with transaction.atomic():
        result = delete_from_given_learning_unit_year(learning_unit_year_to_delete)
    return result


# TODO :: Use LearningUnitPostponementForm to extend/shorten a LearningUnit and remove all this code
def extend_learning_unit(learning_unit_to_edit, new_academic_year):
    result = []
    last_learning_unit_year = LearningUnitYear.objects.filter(
        learning_unit=learning_unit_to_edit
    ).order_by('academic_year').last()

    _check_extend_partim(last_learning_unit_year, new_academic_year)

    if not new_academic_year:  # If there is no selected academic_year, we take the maximal value
        new_academic_year = AcademicYear.objects.max_adjournment()
        if last_learning_unit_year.is_partim():
            new_academic_year = _get_max_academic_year_for_partim(last_learning_unit_year, new_academic_year)

    with transaction.atomic():
        for ac_year in get_next_academic_years(learning_unit_to_edit, new_academic_year.year):
            new_luy = duplicate_learning_unit_year(last_learning_unit_year, ac_year)
            result.append(create_learning_unit_year_creation_message(new_luy))

    return result


def _get_max_academic_year_for_partim(last_learning_unit_year, new_academic_year):
    full_learning_unit = last_learning_unit_year.parent.learning_unit
    last_full = LearningUnitYear.objects.filter(
        learning_unit=full_learning_unit
    ).order_by('academic_year').last()
    if last_full.academic_year.year < new_academic_year.year:
        new_academic_year = last_full.academic_year
    return new_academic_year


def _check_extend_partim(last_learning_unit_year, new_academic_year):
    no_planned_end = None
    if not new_academic_year:  # If there is no selected academic_year, we take the maximal value
        new_academic_year = AcademicYear.objects.max_adjournment(delta=1)
        no_planned_end = NO_PLANNED_END_DISPLAY

    lu_parent = last_learning_unit_year.parent
    if last_learning_unit_year.is_partim() and lu_parent:
        actual_end_year = _get_actual_end_year(lu_parent.learning_unit).year
        both_no_end_year = no_planned_end and not lu_parent.learning_unit.end_year
        if not both_no_end_year and actual_end_year < new_academic_year.year:
            raise IntegrityError(
                _('The selected end year (%(partim_end_year)s) is greater '
                  'than the end year of the parent %(lu_parent)s') % {
                    'partim_end_year': new_academic_year if not no_planned_end else no_planned_end,
                    'lu_parent': lu_parent.acronym
                }
            )


def _update_end_year_field(lu, year):
    lu.end_year = year
    lu.save()
    return _('Learning unit %(acronym)s successfully updated.') % {
        'acronym': lu.acronym,
    }


def duplicate_learning_unit_year(old_learn_unit_year, new_academic_year):
    duplicated_luy = update_related_object(old_learn_unit_year, 'academic_year', new_academic_year)
    duplicated_luy.attribution_procedure = None
    duplicated_luy.learning_container_year = _duplicate_learning_container_year(
        duplicated_luy,
        new_academic_year,
        old_learn_unit_year
    )
    _duplicate_teaching_material(duplicated_luy)
    _duplicate_cms_data(duplicated_luy)
    duplicated_luy.save()

    _duplicate_external(old_learn_unit_year, duplicated_luy)

    return duplicated_luy


def _duplicate_external(old_learning_unit_year, new_learning_unit_year):
    if old_learning_unit_year.is_external():
        try:
            return update_related_object(
                old_learning_unit_year.externallearningunityear,
                "learning_unit_year",
                new_learning_unit_year,
            )
        # Dirty data
        except LearningUnitYear.DoesNotExist:
            pass  # TODO Maybe we should return a error


def _duplicate_learning_container_year(new_learn_unit_year, new_academic_year, old_learn_unit_year):
    duplicated_lcy = _get_or_create_container_year(new_learn_unit_year, new_academic_year)
    _duplicate_learning_component_year(new_learn_unit_year, old_learn_unit_year)
    duplicated_lcy.save()
    return duplicated_lcy


def _get_or_create_container_year(new_learn_unit_year, new_academic_year):
    queryset = LearningContainerYear.objects.filter(
        academic_year=new_academic_year,
        learning_container=new_learn_unit_year.learning_container_year.learning_container
    )
    # Sometimes, the container already exists, we can directly use it and its entitycontaineryear
    if not queryset.exists():
        duplicated_lcy = update_related_object(
            new_learn_unit_year.learning_container_year,
            'academic_year',
            new_academic_year,
            commit_save=False,
        )
        duplicated_lcy.is_vacant = False
        duplicated_lcy.type_declaration_vacant = None
        _raise_if_entity_version_does_not_exist(duplicated_lcy, new_academic_year)
        duplicated_lcy.save()
    else:
        duplicated_lcy = queryset.get()
        duplicated_lcy.copied_from = new_learn_unit_year.learning_container_year
    return duplicated_lcy


def _raise_if_entity_version_does_not_exist(new_lcy, new_academic_year):
    prefetched_entities_previous_year = Entity.objects.filter(
        pk__in=[ent.id for ent in new_lcy.copied_from.get_map_entity_by_type().values() if ent]
    ).prefetch_related(
        "entityversion_set"
    )
    for entity in prefetched_entities_previous_year:
        if not any(obj.exists_at_specific_date(new_academic_year.end_date) for obj in entity.entityversion_set.all()):
            raise IntegrityError(
                _('The entity %(entity_acronym)s does not exist for the selected academic year %(academic_year)s') % {
                    'entity_acronym': entity.most_recent_acronym,
                    'academic_year': new_academic_year
                })


def _duplicate_learning_component_year(new_learn_unit_year, old_learn_unit_year):
    old_components = old_learn_unit_year.learningcomponentyear_set.all()
    for old_component in old_components:
        new_component = update_related_object(old_component, 'learning_unit_year', new_learn_unit_year)
        _duplicate_learning_class_year(new_component)


def _duplicate_learning_class_year(new_component):
    learning_class_years = LearningClassYear.objects.filter(
        learning_component_year=new_component.copied_from
    ).order_by("acronym")
    for old_learning_class in learning_class_years:
        update_related_object(old_learning_class, 'learning_component_year', new_component)


def _duplicate_teaching_material(duplicated_luy):
    previous_teaching_material = mdl_base.teaching_material.find_by_learning_unit_year(duplicated_luy.copied_from)
    for material in previous_teaching_material:
        update_related_object(material, 'learning_unit_year', duplicated_luy)


def _duplicate_cms_data(duplicated_luy):
    previous_cms_data = TranslatedText.objects.filter(reference=duplicated_luy.copied_from.id)
    for item in previous_cms_data:
        update_related_object(item, 'reference', duplicated_luy.id)


def _check_shorten_partims(learning_unit_to_edit, new_academic_year):
    if not LearningUnitYear.objects.filter(
            learning_unit=learning_unit_to_edit, subtype=learning_unit_year_subtypes.FULL).exists():
        return None

    for lcy in LearningContainerYear.objects.filter(learning_container=learning_unit_to_edit.learning_container):
        for partim in lcy.get_partims_related():
            _check_shorten_partim(learning_unit_to_edit, new_academic_year, partim)


def _check_shorten_partim(learning_unit_to_edit, new_academic_year, partim):
    if _get_actual_end_year(partim.learning_unit).year > new_academic_year.year:
        raise IntegrityError(
            _('The learning unit %(learning_unit)s has a partim %(partim)s with '
              'an end year greater than %(year)s') % {
                'learning_unit': learning_unit_to_edit.acronym,
                'partim': partim.acronym,
                'year': new_academic_year
            }
        )


def _get_actual_end_year(learning_unit_to_edit: LearningUnit) -> AcademicYear:
    proposal = ProposalLearningUnit.objects.filter(
        learning_unit_year__learning_unit=learning_unit_to_edit
    ).exclude(
        type=ProposalType.CREATION.name
    ).first()

    end_year_lu = learning_unit_to_edit.end_year
    if proposal:
        end_year = proposal.initial_data.get('learning_unit').get('end_year')
        if end_year:
            end_year_lu = academic_year.find_academic_year_by_id(end_year)
    return end_year_lu or academic_year.find_academic_year_by_year(compute_max_academic_year_adjournment() + 1)


def _get_new_end_year(new_academic_year: AcademicYear):
    return new_academic_year if new_academic_year else None


def get_next_academic_years(learning_unit_to_edit, year: int):
    end_date = learning_unit_to_edit.end_year.year + 1 if learning_unit_to_edit.end_year else None
    return AcademicYear.objects.filter(year__range=(end_date, year)).order_by('year')


def update_learning_unit_year_with_report(
        luy_to_update: LearningUnitYear,
        fields_to_update: Dict[str, Any],
        entities_by_type_to_update: Dict,
        **kwargs) -> None:
    with_report = kwargs.get('with_report', True)
    override_postponement_consistency = kwargs.get('override_postponement_consistency', False)
    lu_to_consolidate = kwargs.get('lu_to_consolidate', None)

    conflict_report = {}
    if with_report:
        conflict_report = get_postponement_conflict_report(
            luy_to_update,
            override_postponement_consistency=override_postponement_consistency
        )
        luy_to_update_list = conflict_report['luy_without_conflict']
    else:
        luy_to_update_list = [luy_to_update]

    # Update luy which doesn't have conflict
    for luy in luy_to_update_list:
        _update_learning_unit_year(luy, fields_to_update, (luy != luy_to_update), entities_by_type_to_update)

    # Show conflict error if exists
    check_postponement_conflict_report_errors(conflict_report)
    if lu_to_consolidate:
        _report_volume(lu_to_consolidate, luy_to_update_list)
        postpone_teaching_materials(luy_to_update)
        _descriptive_fiche_and_achievements_update(lu_to_consolidate, luy_to_update)


# TODO :: Use LearningUnitPostponementForm to extend/shorten a LearningUnit and remove all this code
def get_postponement_conflict_report(
        luy_start: LearningUnitYear,
        override_postponement_consistency: bool = False) -> Dict[str, List[LearningUnitYear]]:
    """
    This function will return a list of learning unit year (luy_without_conflict) ( > luy_start)
    which doesn't have any conflict. If any conflict found, the variable 'errors' will store it.
    """
    result = {'luy_without_conflict': [luy_start]}
    for luy in luy_start.find_gt_learning_units_year():
        error_list = _check_postponement_conflict(luy_start, luy)
        if error_list and not override_postponement_consistency:
            result['errors'] = error_list
            break
        result['luy_without_conflict'].append(luy)
    return result


# TODO :: Use LearningUnitPostponementForm to extend/shorten a LearningUnit and remove all this code
def check_postponement_conflict_report_errors(conflict_report):
    if conflict_report.get('errors'):
        last_instance_updated = conflict_report.get('luy_without_conflict', [])[-1]
        raise ConsistencyError(
            last_instance_updated,
            conflict_report.get('errors'),
            _('An error occured when updating the learning unit.')
        )


def _update_learning_unit_year(
        luy_to_update: LearningUnitYear,
        fields_to_update: Dict[str, Any],
        with_report: bool,
        entities_to_update_by_type: Dict) -> None:
    fields_to_exclude = ()
    if with_report:
        fields_to_exclude = FIELDS_TO_EXCLUDE_WITH_REPORT

    update_instance_model_from_data(luy_to_update.learning_unit, fields_to_update, exclude=('acronym',))

    luy_to_update.learning_container_year.set_entities(entities_to_update_by_type)

    # Only the subtype FULL can edit the container
    if luy_to_update.subtype == learning_unit_year_subtypes.FULL:
        update_instance_model_from_data(
            luy_to_update.learning_container_year,
            fields_to_update,
            exclude=fields_to_exclude
        )
        acronym_full = fields_to_update.get("acronym")
        if acronym_full:
            update_partim_acronym(acronym_full, luy_to_update)
    update_instance_model_from_data(luy_to_update, fields_to_update,
                                    exclude=fields_to_exclude + ("in_charge",))


def _check_postponement_conflict(luy: LearningUnitYear, next_luy: LearningUnitYear):
    error_list = []
    lcy = luy.learning_container_year
    next_lcy = next_luy.learning_container_year
    error_list.extend(_check_postponement_conflict_on_learning_unit_year(luy, next_luy))
    error_list.extend(_check_postponement_conflict_on_learning_container_year(lcy, next_lcy))
    error_list.extend(_check_postponement_conflict_on_entity_container_year(lcy, next_lcy))
    error_list.extend(_check_postponement_conflict_on_volumes(lcy, next_lcy))
    return error_list


def _check_postponement_conflict_on_learning_unit_year(luy, next_luy):
    fields_to_compare = {
        'acronym': _('Acronym'),
        'specific_title': _('English title proper'),
        'specific_title_english': _('English title proper'),
        'subtype': _('Subtype'),
        'credits': _('credits'),
        'internship_subtype': _('Internship subtype'),
        'status': _('Status'),
        'session': _('Session derogation'),
        'quadrimester': _('Quadrimester'),
        'campus': _('Campus'),
        'language': _('Language'),
    }
    return _get_differences(luy, next_luy, fields_to_compare)


def _check_postponement_conflict_on_learning_container_year(lcy, next_lcy):
    fields_to_compare = {
        'container_type': _('type'),
        'common_title': _('Common title'),
        'common_title_english': _('Common English title'),
        'acronym': _('Acronym'),
        'team': _('Team management')
    }
    return _get_differences(lcy, next_lcy, fields_to_compare)


def _get_differences(obj1, obj2, fields_to_compare):
    field_diff = filter(lambda field: _is_different_value(obj1, obj2, field), fields_to_compare.keys())
    error_list = []
    for field_name in field_diff:
        current_value = getattr(obj1, field_name, None)
        next_year_value = getattr(obj2, field_name, None)
        error_list.append(_("The value of field '%(field)s' is different between year %(year)s - %(value)s "
                            "and year %(next_year)s - %(next_value)s") % {
                              'field': fields_to_compare[field_name],
                              'year': obj1.academic_year,
                              'value': _get_translated_value(current_value),
                              'next_year': obj2.academic_year,
                              'next_value': _get_translated_value(next_year_value)
                          })
    return error_list


def _get_translated_value(value):
    if value is None:
        return NO_DATA
    if isinstance(value, bool):
        return _('yes') if value else _('no')
    return value


# TODO :: should remove this function and add requirement_entity, allocation_entity, additional_entities
# TODO ::  in _check_postponement_conflict_on_learning_container_year
def _check_postponement_conflict_on_entity_container_year(lcy, next_lcy):
    current_entities = lcy.get_map_entity_by_type()
    next_year_entities = next_lcy.get_map_entity_by_type()
    error_list = _check_if_all_entities_exist(
        next_lcy,
        list(filter(lambda entity: entity, next_year_entities.values()))
    )
    entity_type_diff = filter(lambda type: _is_different_value(current_entities, next_year_entities, type),
                              ENTITY_TYPE_LIST)
    for entity_type in entity_type_diff:
        current_entity = current_entities.get(entity_type)
        next_year_entity = next_year_entities.get(entity_type)
        error_list.append(_("The value of field '%(field)s' is different between year %(year)s - %(value)s "
                            "and year %(next_year)s - %(next_value)s") % {
                              'field': _(entity_type.lower()),
                              'year': lcy.academic_year,
                              'value': current_entity.most_recent_acronym if current_entity else NO_DATA,
                              'next_year': next_lcy.academic_year,
                              'next_value': next_year_entity.most_recent_acronym if next_year_entity else NO_DATA
                          })
    return error_list


def _check_if_all_entities_exist(lcy, entities_list):
    error_list = []
    date = lcy.academic_year.start_date
    entities_ids = [entity.id for entity in entities_list]
    existing_entities = mdl_base.entity.find_versions_from_entites(entities_ids, date).values_list('id', flat=True)
    entities_not_found = filter(lambda entity: entity.id not in existing_entities, entities_list)

    for entity_not_found in set(entities_not_found):
        error = _("The entity '%(acronym)s' doesn't exist anymore in %(year)s" % {
            'acronym': entity_not_found.most_recent_acronym,
            'year': lcy.academic_year
        })
        error_list.append(error)
    return error_list


def _is_different_value(obj1, obj2, field, empty_str_as_none=True):
    value_obj1 = _get_value_from_field(obj1, field)
    value_obj2 = _get_value_from_field(obj2, field)
    if empty_str_as_none:
        value_obj1 = value_obj1 or ''
        value_obj2 = value_obj2 or ''
    return value_obj1 != value_obj2


def _get_value_from_field(obj, field):
    return obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)


def _check_postponement_conflict_on_volumes(lcy, next_lcy):
    current_learning_units = learning_unit_year_with_context.get_with_context(learning_container_year_id=lcy.id)
    next_year_learning_units = learning_unit_year_with_context.get_with_context(learning_container_year_id=next_lcy.id)

    error_list = []
    for luy_with_components in current_learning_units:
        try:
            next_luy_with_components = _get_next_luy_with_components(luy_with_components, next_year_learning_units)
            if next_luy_with_components:
                error_list.extend(_check_postponement_conflict_on_components(
                    luy_with_components,
                    next_luy_with_components)
                )
        except StopIteration:
            error_list.append(_("There is not the learning unit %(acronym)s - %(next_year)s") % {
                'acronym': luy_with_components.acronym,
                'next_year': next_lcy.academic_year
            })
    return error_list


def _get_next_luy_with_components(luy_with_components, next_year_learning_units):
    return next(
        (luy for luy in next_year_learning_units if luy.learning_unit == luy_with_components.learning_unit),
        None
    )


def _check_postponement_conflict_on_components(luy_with_components, next_luy_with_components):
    error_list = []

    current_components = getattr(luy_with_components, 'components', {})
    next_year_components = getattr(next_luy_with_components, 'components', {})
    for component, volumes_computed in current_components.items():
        try:
            # Get the same component for next year (Key: component type)
            next_year_component = _get_next_year_component(next_year_components, component.type)
            error_list.extend(_check_postponement_conflict_on_volumes_data(
                component, next_year_component,
                volumes_computed, next_year_components[next_year_component]
            ))
            # Pop the values when validation done
            next_year_components.pop(next_year_component)
        except StopIteration:
            # Case current year have component which doesn't exist on next year
            error = _get_error_component_not_found(luy_with_components.acronym, component.type,
                                                   luy_with_components.academic_year,
                                                   next_luy_with_components.academic_year)
            error_list.append(error)

    if next_year_components:
        # Case next year have component which doesn't exist on current year
        for component in next_year_components.keys():
            error_list.append(_get_error_component_not_found(luy_with_components.acronym, component.type,
                                                             next_luy_with_components.academic_year,
                                                             luy_with_components.academic_year))
    return error_list


def _get_next_year_component(next_year_components, component_type):
    return next(next_year_component for next_year_component in next_year_components
                if next_year_component.type == component_type)


def _check_postponement_conflict_on_volumes_data(current_component, next_year_component,
                                                 current_volumes_data, next_year_volumes_data):
    error_list = []
    volumes_fields_diff = _get_volumes_diff(current_volumes_data, next_year_volumes_data)
    for field in volumes_fields_diff:
        values_diff = {'current': current_volumes_data.get(field), 'next_year': next_year_volumes_data.get(field)}
        error_list.append(_get_error_volume_field_diff(field, current_component, next_year_component, values_diff))
    return error_list


def _get_volumes_diff(current_volumes_data, next_year_volumes_data):
    return filter(lambda data: _is_different_value(current_volumes_data, next_year_volumes_data, data),
                  current_volumes_data)


def _get_error_volume_field_diff(field_diff, current_component, next_year_component, values_diff):
    current_value = values_diff.get('current')
    next_value = values_diff.get('next_year')
    return _(
        "The value of field '%(field)s' for the learning unit %(acronym)s (%(component_type)s) "
        "is different between year %(year)s - %(value)s and year %(next_year)s - %(next_value)s"
    ) % {
               'field': COMPONENT_DETAILS[field_diff].lower(),
               'acronym': current_component.learning_unit_year.acronym,
               'component_type': dict(COMPONENT_TYPES)[current_component.type] if current_component.type else 'NT',
               'year': current_component.learning_unit_year.academic_year,
               'value': normalize_fraction(current_value) if current_value is not None else NO_DATA,
               'next_year': next_year_component.learning_unit_year.academic_year,
               'next_value': normalize_fraction(next_value) if next_value is not None else NO_DATA
           }


def _get_error_component_not_found(acronym, component_type, existing_academic_year, not_found_academic_year):
    return _("There is not %(component_type)s for the learning unit %(acronym)s - %(year)s but exist in"
             " %(existing_year)s") % {
               'component_type': _(component_type),
               'acronym': acronym,
               'year': not_found_academic_year,
               'existing_year': existing_academic_year
           }


class ConsistencyError(Error):
    def __init__(self, last_instance_updated, error_list, *args, **kwargs):
        self.last_instance_updated = last_instance_updated
        self.error_list = error_list
        super().__init__(*args, **kwargs)


def create_learning_unit_year_creation_message(learning_unit_year_created):
    link = reverse("learning_unit", kwargs={'learning_unit_year_id': learning_unit_year_created.id})
    return _("Learning Unit <a href='%(link)s'> %(acronym)s (%(academic_year)s) </a> "
             "successfuly created.") % {'link': link, 'acronym': learning_unit_year_created.acronym,
                                        'academic_year': learning_unit_year_created.academic_year}


def update_partim_acronym(acronym_full, luy_to_update):
    partims = luy_to_update.get_partims_related()
    if partims:
        for partim in partims:
            new_acronym = acronym_full + str(partim.acronym[-1])
            partim.acronym = new_acronym
            partim.save()


def _update_luy_achievements_in_future(ac_year_postponement_range, lu_to_consolidate):
    for code, label in settings.LANGUAGES:
        language = Language.objects.get(code=code[:2].upper())
        achievements = LearningAchievement.objects.filter(
            learning_unit_year_id=lu_to_consolidate.id,
            language=language
        )
        for achievement in achievements:
            update_future_luy_achievement(ac_year_postponement_range, achievement)


def _update_descriptive_fiche(ac_year_postponement_range, lu_to_consolidate, luy_to_update):
    cms_labels = \
        CMS_LABEL_PEDAGOGY_FR_AND_EN + CMS_LABEL_PEDAGOGY_FR_ONLY + CMS_LABEL_SPECIFICATIONS + CMS_LABEL_SUMMARY

    for label_key in cms_labels:
        a_text_label = TextLabel.objects.filter(label=label_key).first()

        for code, label in settings.LANGUAGES:
            a_text = TranslatedText.objects.filter(text_label=a_text_label,
                                                   language=code,
                                                   entity=LEARNING_UNIT_YEAR,
                                                   reference=lu_to_consolidate.id).first()

            cms = {"language": code,
                   "text_label": a_text_label,
                   "text": a_text.text if a_text else None
                   }
            update_future_luy(ac_year_postponement_range, luy_to_update, cms)


def _descriptive_fiche_and_achievements_update(proposal_learning_unit_year: LearningUnitYear,
                                               luy_to_update: LearningUnitYear):
    if not luy_to_update.academic_year.is_past:
        ac_year_postponement_range = get_academic_year_postponement_range(proposal_learning_unit_year)
        _update_descriptive_fiche(ac_year_postponement_range, proposal_learning_unit_year, luy_to_update)
        _update_luy_achievements_in_future(ac_year_postponement_range, proposal_learning_unit_year)


def _report_volume(reference: LearningUnitYear, to_postpone_to: List[LearningUnitYear]) -> None:
    try:
        lecturing_component = LearningComponentYear.objects.get(
            learning_unit_year=reference,
            type=learning_component_year_type.LECTURING
        )
        __report_component(lecturing_component, to_postpone_to)
    except LearningComponentYear.DoesNotExist:
        pass

    try:
        practical_component = LearningComponentYear.objects.get(
            learning_unit_year=reference,
            type=learning_component_year_type.PRACTICAL_EXERCISES
        )
        __report_component(practical_component, to_postpone_to)
    except LearningComponentYear.DoesNotExist:
        pass


def __report_component(reference: LearningComponentYear, to_postpone_to: List[LearningUnitYear]) -> None:
    for learning_unit_year_obj in to_postpone_to:
        LearningComponentYear.objects.update_or_create(
            defaults={
                "planned_classes": reference.planned_classes,
                "hourly_volume_total_annual": reference.hourly_volume_total_annual,
                "hourly_volume_partial_q1": reference.hourly_volume_partial_q1,
                "hourly_volume_partial_q2": reference.hourly_volume_partial_q2,
                "repartition_volume_requirement_entity": reference.repartition_volume_requirement_entity,
                "repartition_volume_additional_entity_1": reference.repartition_volume_additional_entity_1,
                "repartition_volume_additional_entity_2": reference.repartition_volume_additional_entity_2,
            },
            learning_unit_year=learning_unit_year_obj,
            type=reference.type,
        )
