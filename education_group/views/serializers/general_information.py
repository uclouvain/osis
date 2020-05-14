from django.conf import settings
from django.db.models import OuterRef, Subquery, fields, F

from base.business.education_groups import general_information_sections
from base.models.education_group_publication_contact import EducationGroupPublicationContact
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from program_management.ddd.domain.node import NodeGroupYear


def get_sections(node: NodeGroupYear, language_code: str):
    translated_labels = __get_translated_labels(node, language_code)
    labels = __get_labels(node)

    sections = {}
    for section in general_information_sections.SECTION_LIST:
        for label in filter(lambda l: l in labels, section.labels):
            translated_label = next(
                translated_label for translated_label in translated_labels if
                translated_label['label_id'] == label
            )
            sections.setdefault(section.title, []).append(translated_label)
    return sections


def __get_translated_labels(node: NodeGroupYear, language_code: str):
    subqstranslated_fr = TranslatedText.objects.filter(reference=node.pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_FR).values('text')[:1]
    subqstranslated_en = TranslatedText.objects.filter(reference=node.pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_EN).values('text')[:1]
    subqslabel = TranslatedTextLabel.objects.filter(
        text_label=OuterRef('pk'),
        language=language_code
    ).values('label')[:1]

    return TextLabel.objects.filter(
        label__in=__get_labels(node)
    ).annotate(
        label_id=F('label'),
        label_translated=Subquery(subqslabel, output_field=fields.CharField()),
        text_fr=Subquery(subqstranslated_fr, output_field=fields.CharField()),
        text_en=Subquery(subqstranslated_en, output_field=fields.CharField())
    ).values('label_id', 'label_translated', 'text_fr', 'text_en')


def __get_labels(node: NodeGroupYear):
    return general_information_sections.SECTIONS_PER_OFFER_TYPE[node.category.name]['specific']


def get_contacts(node: NodeGroupYear):
    qs = EducationGroupPublicationContact.objects.filter(
        education_group_year__educationgroupversion__root_group__element__pk=node.pk
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
