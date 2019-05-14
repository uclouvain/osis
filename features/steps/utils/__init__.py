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

    def count_result(self):
        text = self.find_element(By.CSS_SELECTOR, "#main > div.panel.panel-default > div > strong")
        return text.split()[0]
