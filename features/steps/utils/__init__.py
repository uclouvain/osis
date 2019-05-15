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
import pypom
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class Field:
    def __init__(self, *locator):
        self.locator = locator


class InputField(Field):
    def __set__(self, obj, value):
        element = obj.find_element(*self.locator)
        element.clear()
        if value is not None:
            element.send_keys(value)

    def __get__(self, obj, owner):
        element = obj.find_element(*self.locator)
        return element.get_attribute('value')


class SelectField(Field):
    def __set__(self, obj, text):
        element = Select(obj.find_element(*self.locator))
        element.select_by_visible_text(text)

    def __get__(self, obj, owner):
        element = Select(obj.find_element(*self.locator))
        return element.first_selected_option


class SubmitField(Field):
    def __get__(self, obj, owner):
        return obj.find_element(*self.locator)


class ButtonField(Field):
    def __get__(self, obj, owner):
        return obj.find_element(*self.locator)


class CharField(Field):
    def __get__(self, obj, owner):
        return obj.find_element(*self.locator).text


class Checkbox(Field):
    def __set__(self, obj, value: bool):
        element = obj.find_element(*self.locator)
        old_val = element.get_attribute('checked')
        if not old_val and value:
            element.click()
        elif old_val and not value:
            element.click()


class LoginPage(pypom.Page):
    URL_TEMPLATE = '/login/'

    username = InputField(By.ID, 'id_username')
    password = InputField(By.ID, 'id_password')
    submit = SubmitField(By.ID, 'post_login_btn')

    def login(self, username, password='password123'):
        self.username = username
        self.password = password
        self.submit.click()


class SearchLearningUnitPage(pypom.Page):
    URL_TEMPLATE = '/learning_units/by_activity/'

    anac = SelectField(By.ID, 'id_academic_year_id')
    acronym = InputField(By.ID, 'id_acronym')
    tutor = InputField(By.ID, 'id_tutor')
    requirement_entity = InputField(By.ID, 'id_requirement_entity_acronym')
    container_type = SelectField(By.ID, 'id_container_type')
    clear_button = ButtonField(By.ID, 'btn_clear_filter')
    search = SubmitField(By.CSS_SELECTOR, '#search_form > div > div:nth-child(2) > div.col-md-1 > div > button')
    export = ButtonField(By.ID, "dLabel")
    list_learning_units = ButtonField(By.ID, "btn_produce_xls_with_parameters")
    with_program = ButtonField(By.ID, "chb_with_grp")
    with_tutor = ButtonField(By.ID, "chb_with_attributions")
    generate_xls = ButtonField(By.ID, "btn_xls_with_parameters")

    def count_result(self):
        text = self.find_element(By.CSS_SELECTOR, "#main > div.panel.panel-default > div > strong").text
        return text.split()[0]

    def find_acronym_in_table(self, row: int = 1, col: int = 2):
        selector = '// *[ @ id = "table_learning_units"] / tbody / tr[{}] / td[{}] / a'.format(row, col)
        return self.find_element(By.XPATH, selector).text


class LearningUnitPage(pypom.Page):
    actions = ButtonField(By.ID, "dLabel")
    edit_button = ButtonField(By.CSS_SELECTOR, "#link_edit_lu > a")

    def is_li_edit_link_disabled(self):
        return "disabled" in self.find_element(By.ID, "link_edit_lu").get_attribute("class")


class LearningUnitEditPage(pypom.Page):
    actif = Checkbox(By.ID, "id_status")
    volume_q1_pour_la_partie_magistrale = InputField(By.ID, "id_component-0-hourly_volume_partial_q1")
    volume_q1_pour_la_partie_pratique = InputField(By.ID, "id_component-1-hourly_volume_partial_q1")
    volume_q2_pour_la_partie_magistrale = InputField(By.ID, "id_component-0-hourly_volume_partial_q2")
    volume_q2_pour_la_partie_pratique = InputField(By.ID, "id_component-1-hourly_volume_partial_q2")
    quadrimestre = SelectField(By.ID, "id_quadrimester")
    session_derogation = SelectField(By.ID, "id_session")

    save_button = ButtonField(By.CSS_SELECTOR,
                              "#main > div.panel.panel-default > div.panel-heading > div > div > button")

    no_postponement = ButtonField(By.ID, "btn_without_postponement")
