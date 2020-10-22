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
from collections import OrderedDict
from typing import List

from django.conf import settings
from django.db.models import OuterRef, Subquery, fields, F

from base.business.education_groups import general_information_sections
from base.models.education_group_publication_contact import EducationGroupPublicationContact
from base.models.education_group_year import EducationGroupYear
from base.models.enums.education_group_types import TrainingType
from cms.enums import entity_name
from cms.models import translated_text
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.ddd.domain.group import Group


def get_sections_of_common(year: int, language_code: str):
    reference_pk = EducationGroupYear.objects.get_common(academic_year__year=year).pk
    labels = general_information_sections.SECTIONS_PER_OFFER_TYPE['common']['specific']
    # TODO: Fix me remove this line. We have create this dummy empty group to ensure that algorithm works
    empty_group_node = Group(
        entity_id=None,
        entity_identity=None,
        type=TrainingType.PGRM_MASTER_120,
        abbreviated_title=None,
        titles=None,
        credits=None,
        content_constraint=None,
        management_entity=None,
        teaching_campus=None,
        remark=None,
        start_year=None,
        end_year=None,
    )
    translated_labels = __get_translated_labels(reference_pk, labels, language_code, empty_group_node)
    sections = OrderedDict()
    for section in general_information_sections.SECTION_LIST:
        for label in filter(lambda l: l in labels, section.labels):
            translated_label = translated_labels.get(label)
            sections.setdefault(section.title, []).append(translated_label)
    return sections


def get_sections(group: Group, language_code: str):
    translated_labels = __get_specific_translated_labels(group, language_code)
    common_translated_labels = __get_common_translated_labels(group, language_code)
    labels = set(__get_common_labels(group) + __get_specific_labels(group))

    sections = OrderedDict()
    for section in general_information_sections.SECTION_LIST:
        for label in filter(lambda l: l in labels, section.labels):
            common_translated_label = common_translated_labels.get(label)
            translated_label = translated_labels.get(label)

            if common_translated_label:
                common_translated_label['common_label'] = True
                sections.setdefault(section.title, []).append(common_translated_label)
            if translated_label:
                sections.setdefault(section.title, []).append(translated_label)
    return sections


def __get_specific_translated_labels(group: Group, language_code: str):
    labels = __get_specific_labels(group)
    reference_pk = translated_text.get_groups_or_offers_cms_reference_object(group).pk

    return __get_translated_labels(reference_pk, labels, language_code, group)


def __get_specific_labels(group: Group) -> List[str]:
    return general_information_sections.SECTIONS_PER_OFFER_TYPE[group.type.name]['specific']


def __get_common_translated_labels(group: Group, language_code: str):
    labels = __get_common_labels(group)
    try:
        reference_pk = EducationGroupYear.objects.get_common(academic_year__year=group.year).pk
        translated_labels = __get_translated_labels(reference_pk, labels, language_code, group)
    except EducationGroupYear.DoesNotExist:
        translated_labels = {}
    return translated_labels


def __get_common_labels(group: Group) -> List[str]:
    return general_information_sections.SECTIONS_PER_OFFER_TYPE[group.type.name]['common']


def __get_translated_labels(reference_pk: int, labels: List[str], language_code: str, group: Group):
    entity = entity_name.get_offers_or_groups_entity_from_group(group)
    subqstranslated_fr = TranslatedText.objects.filter(
        reference=reference_pk, text_label=OuterRef('pk'),
        language=settings.LANGUAGE_CODE_FR, entity=entity
    ).values('text')[:1]
    subqstranslated_en = TranslatedText.objects.filter(
        reference=reference_pk, text_label=OuterRef('pk'),
        language=settings.LANGUAGE_CODE_EN, entity=entity
    ).values('text')[:1]
    subqslabel = TranslatedTextLabel.objects.filter(
        text_label=OuterRef('pk'),
        language=language_code
    ).values('label')[:1]

    qs = TextLabel.objects.filter(
        label__in=labels,
        entity=entity
    ).annotate(
        label_id=F('label'),
        label_translated=Subquery(subqslabel, output_field=fields.CharField()),
        text_fr=Subquery(subqstranslated_fr, output_field=fields.CharField()),
        text_en=Subquery(subqstranslated_en, output_field=fields.CharField())
    ).values('label_id', 'label_translated', 'text_fr', 'text_en')

    return {label['label_id']: label for label in qs}


def get_contacts(group: Group):
    qs = EducationGroupPublicationContact.objects.filter(
        education_group_year__educationgroupversion__root_group__partial_acronym=group.code,
        education_group_year__educationgroupversion__root_group__academic_year__year=group.year
    )
    contacts_by_type = {}
    for publication_contact in qs:
        contact_formated = __get_contact_formated(publication_contact)
        contacts_by_type.setdefault(publication_contact.type, []).append(contact_formated)
    return contacts_by_type


def __get_contact_formated(publication_contact):
    return {
        "pk": publication_contact.pk,
        "email": publication_contact.email,
        "description": publication_contact.description,
        "role_fr": publication_contact.role_fr,
        "role_en": publication_contact.role_en,
    }
