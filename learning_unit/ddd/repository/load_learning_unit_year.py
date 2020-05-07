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

from typing import List

from django.db.models import F, Subquery, OuterRef

from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.learning_container_year_types import LearningContainerYearType
from base.models.enums.quadrimesters import DerogationQuadrimester
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_unit_year import LearningUnitYear as LearningUnitYearModel
from learning_unit.ddd.domain.learning_unit_year import LearningUnitYear, LecturingVolume, PracticalVolume
from learning_unit.ddd.domain.description_fiche import DescriptionFiche
from learning_unit.ddd.domain.specifications import Specifications
from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_SPECIFICATIONS
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.translated_text import TranslatedText
from django.db.models import QuerySet
from learning_unit.ddd.repository.load_achievement import load_achievements
from django.conf import settings


def __instanciate_volume_domain_object(learn_unit_data: dict) -> dict:
    learn_unit_data['lecturing_volume'] = LecturingVolume(total_annual=learn_unit_data.pop('pm_vol_tot'))
    learn_unit_data['practical_volume'] = PracticalVolume(total_annual=learn_unit_data.pop('pp_vol_tot'))
    return learn_unit_data


def load_multiple(learning_unit_year_ids: List[int]) -> List['LearningUnitYear']:
    subquery_component = LearningComponentYear.objects.filter(
        learning_unit_year_id=OuterRef('pk')
    )
    subquery_component_pm = subquery_component.filter(
        type=LECTURING
    )
    subquery_component_pp = subquery_component.filter(
        type=PRACTICAL_EXERCISES
    )

    qs = LearningUnitYearModel.objects.filter(pk__in=learning_unit_year_ids).annotate(
        specific_title_en=F('specific_title_english'),
        specific_title_fr=F('specific_title'),
        common_title_fr=F('learning_container_year__common_title'),
        common_title_en=F('learning_container_year__common_title_english'),
        year=F('academic_year__year'),
        proposal_type=F('proposallearningunit__type'),
        start_year=F('learning_unit__start_year'),
        end_year=F('learning_unit__end_year'),
        type=F('learning_container_year__container_type'),
        other_remark=F('learning_unit__other_remark'),

        # components (volumes) data
        pm_vol_tot=Subquery(subquery_component_pm.values('hourly_volume_total_annual')[:1]),
        pp_vol_tot=Subquery(subquery_component_pp.values('hourly_volume_total_annual')[:1]),

    ).values(
        'id',
        'year',
        'acronym',
        'type',
        'specific_title_fr',
        'specific_title_en',
        'common_title_fr',
        'common_title_en',
        'start_year',
        'end_year',
        'proposal_type',
        'credits',
        'status',
        'periodicity',
        'other_remark',
        'quadrimester',

        'pm_vol_tot',
        'pp_vol_tot'

    )

    qs = _annotate_with_description_fiche_specifications(qs)

    results = []

    for learning_unit_data in qs:
        luy = LearningUnitYear(
            __instanciate_volume_domain_object(__convert_string_to_enum(learning_unit_data)),
            achievements=load_achievements(learning_unit_data['acronym'], learning_unit_data['year']),
            description_fiche=DescriptionFiche(
                resume=learning_unit_data.get('cms_resume'),
                resume_en=learning_unit_data.get('cms_resume_en'),
                teaching_methods=learning_unit_data.get('cms_teaching_methods'),
                teaching_methods_en=learning_unit_data.get('cms_teaching_methods_en'),
                evaluation_methods=learning_unit_data.get('cms_evaluation_methods'),
                evaluation_methods_en=learning_unit_data.get('cms_evaluation_methods_en'),
                other_informations=learning_unit_data.get('cms_other_informations'),
                other_informations_en=learning_unit_data.get('cms_other_informations_en'),
                online_resources=learning_unit_data.get('cms_online_resources'),
                online_resources_en=learning_unit_data.get('cms_online_resources_en'),
                bibliography=learning_unit_data.get('cms_bibliography'),
                mobility=learning_unit_data.get('cms_mobility')
            ),
            specifications=Specifications(
                themes_discussed=learning_unit_data.get('cms_themes_discussed'),
                themes_discussed_en=learning_unit_data.get('cms_themes_discussed_en'),
                prerequisite=learning_unit_data.get('cms_prerequisite'),
                prerequisite_en=learning_unit_data.get('cms_prerequisite_en')
            )
        )

        results.append(luy)
    return results


def __convert_string_to_enum(learn_unit_data: dict) -> dict:
    subtype_str = learn_unit_data['type']
    learn_unit_data['type'] = LearningContainerYearType[subtype_str]
    if learn_unit_data.get('quadrimester'):
        learn_unit_data['quadrimester'] = DerogationQuadrimester[learn_unit_data['quadrimester']]
    return learn_unit_data


def _annotate_with_description_fiche_specifications(original_qs1):
    original_qs = original_qs1
    sq = TranslatedText.objects.filter(
        reference=OuterRef('pk'),
        entity=LEARNING_UNIT_YEAR)

    annotations = build_annotations(sq, CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN)
    original_qs = original_qs.annotate(**annotations)

    annotations = build_annotations(sq, CMS_LABEL_SPECIFICATIONS, CMS_LABEL_SPECIFICATIONS)
    original_qs = original_qs.annotate(**annotations)

    return original_qs


def build_annotations(qs: QuerySet, fr_labels: list, en_labels: list):
    annotations = {
        "cms_{}".format(lbl): Subquery(
            _build_subquery_text_label(qs, lbl, settings.LANGUAGE_CODE_FR))
        for lbl in fr_labels
    }

    annotations.update({
        "cms_{}_en".format(lbl): Subquery(
            _build_subquery_text_label(qs, lbl, settings.LANGUAGE_CODE_EN))
        for lbl in en_labels}
    )
    return annotations


def _build_subquery_text_label(qs, cms_text_label, lang):

    return qs.filter(text_label__label="{}".format(cms_text_label), language=lang).values(
        'text')[:1]
