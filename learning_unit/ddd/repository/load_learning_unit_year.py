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
from django.conf import settings
from base.business.learning_unit import CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN, CMS_LABEL_SPECIFICATIONS
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.translated_text import TranslatedText
from django.db.models import QuerySet
from base.models.learning_achievement import LearningAchievement
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
    # TODO il y a qq ch ici qui coince.
    # on peut le constater quand on exécute le test python manage.py test learning_unit.tests.ddd.repository.test_load_learning_unit_year.TestLoadLearningUnitDescriptionFiche.test_load_resume -k
    # malheureusement je vois pas trop ce qui coince....je sais pas si c'est le test ou le query ici
    # Pourrais-tu m'aider?
    # Je suis partie de ce qu'il y avait dans la génération de la liste xls des ue d'une of
    qs = _annotate_with_description_fiche_specifications(qs)

    results = []

    for learnin_unit_data in qs:
        print('yyyyyyyyy')
        print(learnin_unit_data)
        luy = LearningUnitYear(**__instanciate_specific_objects(__convert_string_to_enum(learnin_unit_data)),
                               achievements=load_achievements(learnin_unit_data['acronym'], learnin_unit_data['year']))

        results.append(luy)
    return results


def __convert_string_to_enum(learn_unit_data: dict) -> dict:
    subtype_str = learn_unit_data['type']
    learn_unit_data['type'] = LearningContainerYearType[subtype_str]
    if learn_unit_data.get('quadrimester'):
        learn_unit_data['quadrimester'] = DerogationQuadrimester[learn_unit_data['quadrimester']]
    print('jjj')
    return learn_unit_data


def _annotate_with_description_fiche_specifications(original_qs1):
    original_qs = original_qs1
    sq = TranslatedText.objects.filter(
        reference=OuterRef('pk'),
        entity=LEARNING_UNIT_YEAR)

    annotations = build_annotations(sq, CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN)
    original_qs = original_qs.annotate(**annotations)

    # annotations = build_annotations(sq, CMS_LABEL_SPECIFICATIONS, CMS_LABEL_SPECIFICATIONS)
    # original_qs = original_qs.annotate(**annotations)

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


def __instanciate_specific_objects(learn_unit_data: dict) -> dict:
    __instanciate_volume_domain_object(learn_unit_data)
    __instanciate_description_fiche(learn_unit_data)
    __instanciate_specifications(learn_unit_data)
    return learn_unit_data


def __instanciate_description_fiche(learn_unit_data: dict) -> dict:
    print('__instanciate_description_fiche')
    learn_unit_data['description_fiche'] = None
    # print(learn_unit_data.get('cms_resume'))
    # print(learn_unit_data.get('cms_resume_en'))
    learn_unit_data['description_fiche'] = DescriptionFiche(
        resume=learn_unit_data.get('cms_resume', None),
        resume_en=learn_unit_data.get('cms_resume_en', None),
        teaching_methods=learn_unit_data.pop('cms_teaching_methods') if learn_unit_data.get('cms_teaching_methods') else None,
        teaching_methods_en=learn_unit_data.pop('cms_teaching_methods_en') if learn_unit_data.get('cms_teaching_methods_en') else None,
        evaluation_methods=learn_unit_data.pop('cms_evaluation_methods') if learn_unit_data.get('cms_evaluation_methods') else None,
        evaluation_methods_en=learn_unit_data.pop('cms_evaluation_methods_en') if learn_unit_data.get('cms_cms_evaluation_methods_enresume_en') else None,
        other_informations=learn_unit_data.pop('cms_other_informations') if learn_unit_data.get('cms_other_informations') else None,
        other_informations_en=learn_unit_data.pop('cms_other_informations_en') if learn_unit_data.get('cms_other_informations_en') else None,
        online_resources=learn_unit_data.pop('cms_online_resources') if learn_unit_data.get('cms_online_resources') else None,
        online_resources_en=learn_unit_data.pop('cms_online_resources_en') if learn_unit_data.get('cms_online_resources_en') else None,
        bibliography=learn_unit_data.pop('cms_bibliography') if learn_unit_data.get('cms_bibliography') else None,
        mobility=learn_unit_data.pop('cms_mobility') if learn_unit_data.get('cms_mobility') else None,
    )
    return learn_unit_data


def __instanciate_specifications(learn_unit_data: dict) -> dict:
    print('__instanciate_specifications')
    learn_unit_data['specifications'] = None
    learn_unit_data['specifications'] = Specifications(
        themes_discussed=learn_unit_data.pop('cms_themes_discussed') if learn_unit_data.get('cms_themes_discussed') else None,
        themes_discussed_en=learn_unit_data.pop('cms_themes_discussed_en') if learn_unit_data.get('cms_themes_discussed_en') else None,
        prerequisite=learn_unit_data.pop('cms_prerequisite') if learn_unit_data.get('cms_prerequisite') else None,
        prerequisite_en=learn_unit_data.pop('cms_prerequisite_en') if learn_unit_data.get('cms_prerequisite_en') else None,
    )
    return learn_unit_data
