from django.conf import settings
from django.db.models import OuterRef, F, Subquery, fields

from base.business.education_groups import general_information_sections
from base.models.education_group_achievement import EducationGroupAchievement
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from program_management.ddd.domain.node import NodeGroupYear


def get_achievements(node: NodeGroupYear):
    qs = EducationGroupAchievement.objects.filter(
        education_group_year__educationgroupversion__root_group__partial_acronym=node.code,
        education_group_year__educationgroupversion__root_group__academic_year__year=node.year
    ).prefetch_related('educationgroupdetailedachievement_set')

    achievements = []
    for achievement in qs:
        achievements.append({
            **__get_achievement_formated(achievement),
            'detailed_achievements': [
                __get_achievement_formated(d_achievement) for d_achievement
                in achievement.educationgroupdetailedachievement_set.all()
            ]
        })
    return achievements


def __get_achievement_formated(achievement):
    return {
        'pk': achievement.pk,
        'code_name': achievement.code_name,
        'text_fr': achievement.french_text,
        'text_en': achievement.english_text
    }


def get_skills_labels(node: NodeGroupYear, language_code: str):
    subqstranslated_fr = TranslatedText.objects.filter(reference=node.pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_FR).values('text')[:1]
    subqstranslated_en = TranslatedText.objects.filter(reference=node.pk, text_label=OuterRef('pk'),
                                                       language=settings.LANGUAGE_CODE_EN).values('text')[:1]
    subqslabel = TranslatedTextLabel.objects.filter(
        text_label=OuterRef('pk'),
        language=language_code
    ).values('label')[:1]

    return TextLabel.objects.filter(
        label__in=[
            general_information_sections.CMS_LABEL_PROGRAM_AIM,
            general_information_sections.CMS_LABEL_ADDITIONAL_INFORMATION
        ]
    ).annotate(
        label_id=F('label'),
        label_translated=Subquery(subqslabel, output_field=fields.CharField()),
        text_fr=Subquery(subqstranslated_fr, output_field=fields.CharField()),
        text_en=Subquery(subqstranslated_en, output_field=fields.CharField())
    ).values('label_id', 'label_translated', 'text_fr', 'text_en')
