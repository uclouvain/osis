# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
import datetime

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import translation
from django.views.generic import FormView
from waffle.decorators import waffle_switch

from base.forms.education_group.common import SelectLanguage
from base.models.enums.education_group_types import GroupType
from base.views.mixins import FlagMixin, AjaxTemplateMixin
from osis_common.document.pdf_build import render_pdf
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.domain.service.identity_search import ProgramTreeVersionIdentitySearch, \
    ProgramTreeIdentitySearch
from program_management.ddd.repositories.program_tree_version import ProgramTreeVersionRepository
from program_management.ddd.repositories.program_tree import ProgramTreeRepository
from backoffice.settings.base import LANGUAGE_CODE_EN


CURRENT_SIZE_FOR_ANNUAL_COLUMN = 15
MAIN_PART_INIT_SIZE = 650
PADDING = 10
USUAL_NUMBER_OF_BLOCKS = 3


@login_required
@waffle_switch('education_group_year_generate_pdf')
def pdf_content(request, year, code, language):
    node_id = NodeIdentity(code=code, year=year)

    program_tree_id = ProgramTreeVersionIdentitySearch().get_from_node_identity(node_id)
    program_tree_version = ProgramTreeVersionRepository.get(program_tree_id)
    if program_tree_version:
        tree = program_tree_version.get_tree()
    else:
        tree = ProgramTreeRepository.get(
            ProgramTreeIdentitySearch().get_from_node_identity(node_id)
        )
    tree = tree.prune(ignore_children_from={GroupType.MINOR_LIST_CHOICE})

    if language == LANGUAGE_CODE_EN:
        title = tree.root_node.group_title_en
    else:
        title = tree.root_node.group_title_fr
    if program_tree_version and program_tree_version.version_label:
        file_name_version_label = "_{}".format(title, program_tree_version.version_label)
        title = "{} - Version {}".format(title, program_tree_version.version_label)
    else:
        file_name_version_label = None

    context = {
        'root': tree.root_node,
        'tree': tree.root_node.children,
        'language': language,
        'created': datetime.datetime.now(),
        'max_block': tree.get_greater_block_value(),
        'main_part_col_length': get_main_part_col_length(tree.get_greater_block_value()),
        'title': title
    }

    with translation.override(language):
        return render_pdf(
            request,
            context=context,
            filename=_build_file_name(file_name_version_label, program_tree_version, tree.root_node.title),
            template='pdf_content.html',
        )


class ReadEducationGroupTypeView(FlagMixin, AjaxTemplateMixin, FormView):
    flag = "pdf_content"
    template_name = "group_element_year/pdf_content.html"
    form_class = SelectLanguage

    def form_valid(self, form):
        self.kwargs['language'] = form.cleaned_data['language']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(pdf_content, kwargs=self.kwargs)


def get_main_part_col_length(max_block):
    if max_block <= USUAL_NUMBER_OF_BLOCKS:
        return MAIN_PART_INIT_SIZE
    else:
        return MAIN_PART_INIT_SIZE - ((max_block-USUAL_NUMBER_OF_BLOCKS) * (CURRENT_SIZE_FOR_ANNUAL_COLUMN + PADDING))


def _build_file_name(file_name_version_label, program_tree_version, title):
    if program_tree_version:
        return "{}{}".format(
            program_tree_version.entity_id.offer_acronym,
            file_name_version_label if file_name_version_label else ''
        )

    return title
