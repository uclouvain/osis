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

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


class Select2Field(Field):
    sub_input_locator = "select2-search__field"

    def __set__(self, obj, value):
        element = obj.find_element(*self.locator)
        element.click()

        sub_element = obj.find_element(By.CLASS_NAME, self.sub_input_locator)
        sub_element.clear()

        if value is not None:
            sub_element.send_keys(value)
        time.sleep(1)
        sub_element.send_keys(Keys.RETURN)


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
