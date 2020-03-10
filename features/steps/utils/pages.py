# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import time
from abc import ABC

import pypom
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from features.steps.utils.fields import InputField, SubmitField, SelectField, ButtonField, \
    Link, \
    Field, SelectEntityVersionField


class AjaxModal(pypom.Page, ABC):
    def loaded(self):
        return self.find_element(By.ID, "form-modal-ajax-content")


class SuccessMessageRegion(pypom.Region):
    _root_locator = (By.ID, 'pnl_succes_messages')

    def loaded(self):
        return self.root.is_displayed()

    @property
    def text(self):
        return self.root.text


class CommonPageMixin:
    @property
    def success_messages(self):
        region = SuccessMessageRegion(self)
        region.wait_for_region_to_load()
        return region


class QuickSearchPage(AjaxModal):
    code = InputField(By.ID, 'id_search_text')
    search = ButtonField(By.CSS_SELECTOR, '#form-modal > div > div.col-md-1.col-md-offset-2 > button', 1)
    select_first = ButtonField(
        By.CSS_SELECTOR,
        '#form-modal-ajax-content > div.modal-body > div.row > div > table > tbody > tr > td:nth-child(1) > button'
    )

    lu_tab = ButtonField(By.CSS_SELECTOR, '#form-modal-ajax-content > div.modal-body > ul > li:nth-child(1) > a', 1)

    eg_tab = ButtonField(By.CSS_SELECTOR, '#form-modal-ajax-content > div.modal-body > ul > li:nth-child(2) > a')

    close = Link('EducationGroupPage', By.CSS_SELECTOR, '#form-modal-ajax-content > div.modal-header > button')


class LoginPage(pypom.Page):
    URL_TEMPLATE = '/login/'

    username = InputField(By.ID, 'id_username')
    password = InputField(By.ID, 'id_password')
    submit = SubmitField(By.ID, 'post_login_btn')

    def login(self, username, password='password123'):
        self.username = username
        self.password = password
        self.submit.click()


class CopyModalPage(AjaxModal):
    copy_btn = Link('AttachModalPage', By.CSS_SELECTOR, '.modal-footer > .btn-primary', 1)


class DetachModalPage(AjaxModal):
    save_modal = Link('EducationGroupPage', By.CSS_SELECTOR, '.modal-footer > .btn-danger', 6)


class AttachModalPage(AjaxModal):
    type_de_lien = SelectField(By.ID, 'id_link_type')
    save_modal = Link('EducationGroupPage', By.CSS_SELECTOR, '.modal-footer > .btn-primary', 6)


class EducationGroupPage(CommonPageMixin, pypom.Page):
    sigleintitule_abrege = Field(
        By.CSS_SELECTOR,
        '#identification > div > div > div.row > div.col-md-7 > div:nth-child(1) > div > div.row > dl:nth-child(1) > dd'
    )
    code = Field(
        By.CSS_SELECTOR,
        '#identification > div > div > div.row > div.col-md-7 > div:nth-child(1) > div > div.row > dl:nth-child(2) > dd'
    )
    entite_de_gestion = Field(
        By.CSS_SELECTOR,
        '#identification > div > div > div.row > div.col-md-5 > div:nth-child(1) > div > dl:nth-child(1) > dd'
    )
    entite_dadministration = Field(
        By.CSS_SELECTOR,
        '#identification > div > div > div.row > div.col-md-5 > div:nth-child(1) > div > dl:nth-child(2) > dd'
    )
    actions = ButtonField(By.ID, 'dLabel')

    modify = Link('UpdateTrainingPage', By.CSS_SELECTOR, '#link_update > a', 1)
    delete = ButtonField(By.CSS_SELECTOR, '#link_delete > a', 1)
    select_first = ButtonField(By.CSS_SELECTOR, "#select_li > a", 1)

    confirm_modal = Link('SearchEducationGroupPage', By.CSS_SELECTOR, '.modal-footer>input[type=submit]')

    toggle_tree = ButtonField(By.CSS_SELECTOR, '#panel-data > div.panel-heading > div > a')
    open_first_node_tree = ButtonField(By.CSS_SELECTOR, '#panel_file_tree > ul > li > i')

    quick_search = Link(QuickSearchPage, By.ID, 'quick-search', 1)
    save_modal = Link('EducationGroupPage', By.CSS_SELECTOR, '.modal-footer > .btn-primary', 4)

    attach = Link(CopyModalPage, By.CSS_SELECTOR, 'body > ul > li:nth-child(4) > a', 2)
    detach = Link(DetachModalPage, By.CSS_SELECTOR, 'body > ul > li:nth-child(5) > a', 2)

    def get_name_first_children(self) -> list:
        children = self.find_elements(By.CSS_SELECTOR, '#panel_file_tree > ul > li > ul > li')
        return [child.text for child in children]

    def find_node_tree_by_acronym(self, acronym, parent=None):
        if not parent:
            parent = self
        else:
            parent = self.find_node_tree_by_acronym(parent)

        for node in parent.find_elements(By.CSS_SELECTOR, 'li.jstree-node'):
            if acronym == node.text.split('-')[0].strip():
                return node
        raise Exception("Node not found")

    def open_node_tree_by_acronym(self, acronym):
        node = self.find_node_tree_by_acronym(acronym)
        node.find_element(By.CSS_SELECTOR, 'i').click()

    def rigth_click_node_tree(self, acronym, parent=None):
        node = self.find_node_tree_by_acronym(acronym, parent)

        action_chains = ActionChains(self.driver)
        child = node.find_element(By.CSS_SELECTOR, 'a')
        action_cains.context_click(child).perform()
        return child

    def attach_node_tree(self, acronym, parent=None):
        self.rigth_click_node_tree(acronym, parent)
        return self.attach.click()

    def detach_node_tree(self, acronym, parent=None):
        self.rigth_click_node_tree(acronym, parent)
        return self.detach.click()

    def select_node_tree(self, acronym, parent=None):
        self.rigth_click_node_tree(acronym, parent)
        self.find_element(By.CSS_SELECTOR, 'body > ul > li:nth-child(1) > a').click()
        time.sleep(1)

    @property
    def loaded(self) -> bool:
        return "Identification" in self.find_element(
            By.CSS_SELECTOR, 'li.active[role=presentation]'
        ).text and not self.find_element(By.ID, 'modal_dialog_id').is_displayed()


class NewTrainingPage(pypom.Page):
    sigleintitule_abrege = InputField(By.ID, 'id_acronym')
    code = InputField(By.ID, 'id_partial_acronym')
    intitule_en_francais = InputField(By.ID, 'id_title')
    intitule_en_anglais = InputField(By.ID, 'id_title_english')
    entite_de_gestion = SelectEntityVersionField(By.ID, 'id_management_entity')
    entite_dadministration = SelectEntityVersionField(By.ID, 'id_administration_entity')
    intitule_du_diplome = InputField(By.ID, 'id_diploma_printing_title')

    tab_diploma = ButtonField(By.ID, 'lnk_diplomas_certificats')
    save_button = Link(EducationGroupPage, By.ID, 'btn-confirm', waiting_time=3)


class UpdateTrainingPage(NewTrainingPage):
    fin = InputField(By.ID, 'id_end_year')


class SearchEducationGroupPage(CommonPageMixin, pypom.Page):
    URL_TEMPLATE = '/educationgroups/'

    sigleintitule_abrege = InputField(By.ID, 'id_acronym')
    code = InputField(By.ID, 'id_partial_acronym')
    anac = SelectField(By.ID, 'id_academic_year')

    actions = ButtonField(By.ID, 'btn-action')
    new_training = ButtonField(By.CSS_SELECTOR, '#link_create_training > a', 1)
    new_mini_training = ButtonField(By.CSS_SELECTOR, '#link_create_mini_training > a', 1)

    first_row = Link('EducationGroupPage', By.CSS_SELECTOR,
                     '#table_education_groups > tbody > tr:nth-child(1) > td:nth-child(2) > a')

    type_de_formation = SelectField(By.ID, "id_name")
    confirm_modal = Link(NewTrainingPage, By.CSS_SELECTOR, '.modal-footer>input.btn-primary')
    clear_button = ButtonField(By.ID, 'btn_clear_filter')
    search = Link('SearchEducationGroupPage', By.CSS_SELECTOR, 'button.btn-primary', 1)

    quick_search = Link(QuickSearchPage, By.ID, 'quick-search', 1)

    def count_result(self):
        text = self.find_element(
            By.CSS_SELECTOR,
            '#main > div.panel.panel-default > div > div > div.row > div:nth-child(1)').text
        return text.split()[0]


class SearchEntityPage(CommonPageMixin, pypom.Page):
    URL_TEMPLATE = '/entities/'

    acronym = InputField(By.ID, 'id_acronym')
    title = InputField(By.ID, 'id_title')
    entity_type = SelectField(By.ID, "id_entity_type")

    search = ButtonField(By.ID, "bt_submit_entity_search")

    def find_acronym_in_table(self, row: int = 1):
        return self.find_element(By.ID, 'td_entity_%d' % row).text


class SearchOrganizationPage(CommonPageMixin, pypom.Page):

    URL_TEMPLATE = '/organizations/'

    acronym = InputField(By.ID, 'id_acronym')
    name = InputField(By.ID, 'id_name')
    type = SelectField(By.ID, "id_type")

    search = ButtonField(By.ID, "bt_submit_organization_search")

    def find_acronym_in_table(self, row: int = 1):
        return self.find_element(By.ID, 'td_organization_%d' % row).text


class SearchStudentPage(CommonPageMixin, pypom.Page):

    URL_TEMPLATE = '/students/'

    registration_id = InputField(By.ID, 'id_registration_id')
    name = InputField(By.ID, 'id_name')

    search = ButtonField(By.ID, "bt_submit_student_search")

    def find_registration_id_in_table(self, row: int = 1):
        return self.find_element(By.ID, 'td_student_%d' % row).text

    def find_name_in_table(self):
        names = []
        row = 1
        last = False
        while not last:
            try:
                elt = self.find_element(By.ID, 'spn_student_name_%d' % row)
                names.append(elt.text)

                row += 1
            except NoSuchElementException as e:
                return names

        return names
