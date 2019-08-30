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
from django.conf import settings
from django.db.models import Prefetch, Case, When, Value, IntegerField
from django.utils.translation import gettext_lazy as _
from openpyxl.styles import Alignment, Style
from openpyxl.utils import get_column_letter

from base.models.person import get_user_interface_language
from base.views.learning_unit import get_specifications_context
from base.business.learning_unit import CMS_LABEL_PEDAGOGY_FR_ONLY, \
    CMS_LABEL_PEDAGOGY, CMS_LABEL_PEDAGOGY_FR_AND_EN
from base.models.teaching_material import TeachingMaterial
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from cms.models.text_label import TextLabel
from base.business.learning_unit_xls import annotate_qs
from base.business.xls import get_name_or_username
from osis_common.document import xls_build
from base.business.learning_unit import CMS_LABEL_SPECIFICATIONS, get_achievements_group_by_language

EN = 'en'
FR_BE = 'fr-be'

XLS_DESCRIPTION = _('Learning units list')
XLS_FILENAME = _('LearningUnitsList')
WORKSHEET_TITLE = _('Learning units list')
WRAP_TEXT_STYLE = Style(alignment=Alignment(wrapText=True, vertical="top"), )


def create_xls_educational_information_and_specifications(user, learning_units, request):

    titles = _get_titles()

    data = prepare_xls_educational_information_and_specifications(learning_units, request)
    working_sheet_data = data.get('data')

    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: titles,
                  xls_build.WS_TITLE: WORKSHEET_TITLE,
                  xls_build.ROW_HEIGHT: {'height': 30,
                                         'start': 2,
                                         'stop': (len(learning_units)) + 1
                                         },
                  xls_build.STYLED_CELLS: {
                      WRAP_TEXT_STYLE: _get_wrapped_cells_educational_information_and_specifications(
                          learning_units, len(titles)
                      )
                  }
                  }

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheet_data, parameters))


def _get_titles():
    titles = [
        str(_('Code')),
        str(_('Title')),
        str(_('Req. Entity')),
    ]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_SPECIFICATIONS, True)
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_PEDAGOGY_FR_AND_EN, True)
    titles = titles + [str(_('Teaching material'))]
    titles = titles + _add_cms_title_fr_en(CMS_LABEL_PEDAGOGY_FR_ONLY, False)
    titles = titles + [str("{} - {}".format('Learning achievements', FR_BE.upper())),
                       str("{} - {}".format(_('Learning achievements'), EN.upper()))]
    return titles


def _add_cms_title_fr_en(cms_labels, with_en=True):
    titles = []
    for label_key in cms_labels:
        a_text_label = TextLabel.objects.filter(label=label_key).first()
        titles.append(_add_text_label(a_text_label, FR_BE))
        if with_en:
            titles.append(_add_text_label(a_text_label, EN))
    return titles


def prepare_xls_educational_information_and_specifications(learning_unit_years, request):
    qs = annotate_qs(learning_unit_years)
    user_language = get_user_interface_language(request.user)

    result = []
    red_cells = []
    border_top = []
    wrapped_cells = []

    for learning_unit_yr in qs:
        translated_labels_with_text = _get_translated_labels_with_text(learning_unit_yr.id, user_language)
        teaching_materials = TeachingMaterial.objects.filter(learning_unit_year=learning_unit_yr).order_by('order')

        line = [
            learning_unit_yr.acronym,
            learning_unit_yr.complete_title,
            learning_unit_yr.entity_requirement,
        ]

        _add_specifications(learning_unit_yr, line, request)

        for label_key in CMS_LABEL_PEDAGOGY_FR_AND_EN:
            translated_label = translated_labels_with_text.filter(text_label__label=label_key).first()
            if translated_label:
                line.append(translated_label.text_label.text_fr[0].text if translated_label.text_label.text_fr else '')
                line.append(translated_label.text_label.text_en[0].text if translated_label.text_label.text_en else '')
            else:
                line.append('')
                line.append('')

        if teaching_materials:
            teaching_material_detail = None
            for teaching_material in teaching_materials:
                if teaching_material_detail is None:
                    teaching_material_detail = ''
                else:
                    teaching_material_detail += "\n"

                teaching_material_detail += teaching_material.title
            line.append(teaching_material_detail)
        else:
            line.append('')

        for label_key in CMS_LABEL_PEDAGOGY_FR_ONLY:
            translated_label = translated_labels_with_text.filter(text_label__label=label_key).first()

            if translated_label:
                line.append(translated_label.text_label.text_fr[0].text if translated_label.text_label.text_fr else '')
            else:
                line.append('')

        line.extend(_add_achievements(learning_unit_yr))

        result.append(line)

    return {
        'data': result,
        'missing_values': red_cells,
        'border_top': border_top,
        'wrapped_cells': wrapped_cells
    }


def _add_achievements(learning_unit_yr):
    achievements = get_achievements_group_by_language(learning_unit_yr)
    return [_add_achievement(achievements.get('achievements_FR', None)),
            _add_achievement(achievements.get('achievements_EN', None))]


def _add_specifications(learning_unit_yr, line, request):
    specifications = get_specifications_context(learning_unit_yr, request)
    obj_fr = specifications.get('form_french')
    obj_en = specifications.get('form_english')
    for label_key in CMS_LABEL_SPECIFICATIONS:
        _add_specification_by_lang(label_key, obj_fr, line)
        _add_specification_by_lang(label_key, obj_en, line)


def _get_translated_labels_with_text(learning_unit_year_id, user_language):
    translated_labels_with_text = TranslatedTextLabel.objects.filter(
        language=user_language,
        text_label__label__in=CMS_LABEL_PEDAGOGY
    ).prefetch_related(
        Prefetch(
            "text_label__translatedtext_set",
            queryset=TranslatedText.objects.filter(
                language=settings.LANGUAGE_CODE_FR,
                entity=LEARNING_UNIT_YEAR,
                reference=learning_unit_year_id
            ),
            to_attr="text_fr"
        ),
        Prefetch(
            "text_label__translatedtext_set",
            queryset=TranslatedText.objects.filter(
                language=settings.LANGUAGE_CODE_EN,
                entity=LEARNING_UNIT_YEAR,
                reference=learning_unit_year_id
            ),
            to_attr="text_en"
        )
    ).annotate(
        label_ordering=Case(
            *[When(text_label__label=label, then=Value(i)) for i, label in enumerate(CMS_LABEL_PEDAGOGY)],
            default=Value(len(CMS_LABEL_PEDAGOGY)),
            output_field=IntegerField()
        )
    ).select_related(
        "text_label"
    ).order_by(
        "label_ordering"
    )
    return translated_labels_with_text


def _add_achievement(achievements):
    achievement_detail = None
    if achievements:
        for achievement in achievements:
            if achievement_detail is None:
                achievement_detail = ''
            else:
                achievement_detail += '\n'
            achievement_detail += achievement.text

        return achievement_detail
    else:
        return ''


def _add_specification_by_lang(label_key, obj_fr, part_fr):
    try:
        french_value = obj_fr.__getattribute__(label_key)
    except AttributeError:
        french_value = None
    if french_value:
        part_fr.append(french_value)
    else:
        part_fr.append('')


def _get_wrapped_cells_educational_information_and_specifications(learning_units, nb_col):
    dict_wrapped_styled_cells = []

    for idx, luy in enumerate(learning_units, start=2):
        column_number = 1
        while column_number <= nb_col:
            dict_wrapped_styled_cells.append("{}{}".format(get_column_letter(column_number), idx))
            column_number += 1
    return dict_wrapped_styled_cells


def _add_text_label(a_text_label, language_code):
    a_label = TranslatedTextLabel.objects.filter(text_label=a_text_label, language=language_code).first()
    return "{} - {}".format(a_label if a_label else '', language_code.upper())
