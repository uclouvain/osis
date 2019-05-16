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

import html

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from openpyxl.styles import Style, Alignment

from base.business.learning_unit import XLS_DESCRIPTION, XLS_FILENAME
from base.business.xls import get_name_or_username
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models.translated_text import TranslatedText
from osis_common.document import xls_build
from osis_common.document.xls_build import prepare_xls_parameters_list

WRAP_TEXT_COLUMNS = ['D', 'F']


def generate_xls_teaching_material(user, learning_units):
    """ Generate a XLS file with all filtered learning_units where the course material is required """

    titles = [
        str(_('code')).title(),
        str(_('Title')),
        str(_('Req. Entity')).title(),
        str(_('bibliography')).title(),
        str(_('teaching materials')).title(),
        str(_('online resources')).title(),
    ]

    rows = [lu for lu in learning_units if lu.teachingmaterial_set.filter(mandatory=True)]

    file_parameters = {
        xls_build.DESCRIPTION: XLS_DESCRIPTION,
        xls_build.FILENAME: XLS_FILENAME,
        xls_build.USER: get_name_or_username(user),
        xls_build.HEADER_TITLES: titles,
        xls_build.WS_TITLE: _("Teaching material"),
        xls_build.STYLED_CELLS: {
            Style(alignment=Alignment(wrap_text=True)): _get_text_wrapped_cells(len(rows)),
        }
    }

    working_sheets_data = _filter_required_teaching_material(learning_units)
    return xls_build.generate_xls(prepare_xls_parameters_list(working_sheets_data, file_parameters))


def _filter_required_teaching_material(learning_units):
    """ Apply a filter to return a list with only the learning units with at least one teaching material """
    result = []
    for learning_unit in learning_units:
        # Only learning_units with a required teaching material will be display
        if not learning_unit.teachingmaterial_set.filter(mandatory=True):
            continue

        # Fetch data in CMS and convert
        bibliography = _get_bibliography(learning_unit)
        online_resources = _get_online_resources(learning_unit)

        result.append((
            learning_unit.acronym,
            learning_unit.complete_title,
            learning_unit.requirement_entity,
            # Let a white space, the empty string is converted in None.
            bibliography if bibliography != "" else " ",
            ", ".join(learning_unit.teachingmaterial_set.filter(mandatory=True).values_list('title', flat=True)),
            online_resources if online_resources != "" else " ",
        ))

    if not result:
        raise ObjectDoesNotExist

    return result


def _hyperlinks_to_string(text):
    """ Extract all hyperlinks and append them to a string using a 'title - [url]' format """
    converted_resources = ""
    soup = BeautifulSoup(text, "html5lib")
    for element in soup.find_all(['a', 'p']):
        if element.name in ['p']:
            converted_resources += "\n" if converted_resources != "" else ""
        else:
            converted_resources += "{} - [{}] \n".format(element.text, element.get('href'))
    # strip tags when no html hyperlink has been found
    if converted_resources == "":
        return _strip_tags(text)
    return converted_resources


def _html_list_to_string(text):
    """ Extract lists and append them to a string keeping the structure """
    converted_text = ""
    soup = BeautifulSoup(text, "html5lib")
    for element in soup.find_all(['ul', 'ol', 'li', 'p']):
        if element.name in ['ul', 'ol', 'p']:
            converted_text += "\n" if converted_text != "" else ""
        else:
            converted_text += "{}\n".format(element.get_text())
    # strip tags when no list has been found
    if converted_text == "":
        return _strip_tags(text)
    return converted_text


def _strip_tags(text):
    soup = BeautifulSoup(text, "html5lib")
    return soup.get_text()


def _get_text_wrapped_cells(count):
    return ['{}{}'.format(col, row) for col in WRAP_TEXT_COLUMNS for row in range(2, count+2)]


def _get_attribute_cms(learning_unit, text_label):
    attr = getattr(TranslatedText.objects.filter(text_label__label=text_label, entity=LEARNING_UNIT_YEAR,
                                                 reference=learning_unit.pk).first(), "text", " ")
    return attr


def _get_online_resources(learning_unit):
    attr = _get_attribute_cms(learning_unit, 'online_resources')
    return _hyperlinks_to_string(html.unescape(attr)) if attr else ""


def _get_bibliography(learning_unit):
    attr = _get_attribute_cms(learning_unit, 'bibliography')
    return _html_list_to_string(html.unescape(attr)) if attr else ""
