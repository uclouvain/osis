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

from features.steps.utils.fields import InputField, SubmitField, SelectField, ButtonField, Checkbox, Select2Field, Link, \
    CkeditorField, RadioField


class LoginPage(pypom.Page):
    URL_TEMPLATE = '/login/'

    username = InputField(By.ID, 'id_username')
    password = InputField(By.ID, 'id_password')
    submit = SubmitField(By.ID, 'post_login_btn')

    def login(self, username, password='password123'):
        self.username = username
        self.password = password
        self.submit.click()


class RepartitionPage(pypom.Page):
    volume_2 = InputField(By.ID, "id_practical_form-allocation_charge")
    save_button = Link('LearningUnitAttributionPage', By.ID, 'save_btn')

    def find_corresponding_button(self, row):
        return self.find_element(By.XPATH, '//*[@id="attributions"]/table/tbody/tr[{}]/td[6]/a'.format(row))


class LearningUnitAttributionPage(pypom.Page):
    manage_repartition = Link(RepartitionPage, By.ID, "manage_repartition")
    save_button = Link('LearningUnitAttributionPage', By.ID, 'save_btn', 2)
    volume_1 = InputField(By.ID, "id_lecturing_form-allocation_charge")

    def find_edit_button(self, row):
        return self.find_element(By.XPATH, '//*[@id="attributions"]/table/tbody/tr[{}]/td[6]/a[1]'.format(row))

    def attribution_row(self, row) -> list:
        result = []

        for i in range(1, 7):
            text = self.find_element(By.XPATH, "//*[@id='attributions']/table/tbody/tr[{}]/td[{}]".format(row, i)).text
            if text:
                result.append(text)

        return result

    @property
    def loaded(self):
        return self.find_element(By.XPATH, '//*[@id="attributions"]/table/thead/tr/th[1]').text == "Enseignant·e·s"


class LearningUnitTrainingPage(pypom.Page):
    def including_groups(self) -> list:
        row_count = len(self.find_elements(By.XPATH, "//*[@id='trainings']/table/tbody/tr"))
        groups = []
        for i in range(1, row_count + 1):
            groups.append(self.find_element(By.XPATH, '//*[@id="trainings"]/table/tbody/tr[{}]/td[1]/a'.format(i)).text)

        return groups

    def enrollments_row(self, row) -> list:
        result = []
        for i in range(1, 4):
            result.append(self.find_element(
                By.XPATH, "//*[@id='learning_unit_enrollments']/table/tbody/tr[{}]/td[{}]".format(
                    row, i)
            ).text)
        return result


class NewLearningUnitPage(pypom.Page):
    _code_0 = SelectField(By.ID, "id_acronym_0")
    _code_1 = InputField(By.ID, "id_acronym_1")

    @property
    def code(self):
        return self._code_0 + self._code_1

    @code.setter
    def code(self, value):
        self._code_0 = value[0]
        self._code_1 = value[1:]

    type = SelectField(By.ID, "id_container_type")
    credit = InputField(By.ID, "id_credits")
    lieu_denseignement = SelectField(By.ID, "id_campus")
    intitule_commun = InputField(By.ID, "id_common_title")
    entite_resp_cahier_des_charges = Select2Field(
        By.XPATH, "//*[@id='LearningUnitYearForm']/div[2]/div[1]/div[2]/div/div/div[3]/div/span")
    entite_dattribution = Select2Field(
        By.XPATH, "//*[@id='LearningUnitYearForm']/div[2]/div[1]/div[2]/div/div/div[4]/div/span")
    save_button = ButtonField(By.NAME, 'learning_unit_year_add')


class NewPartimPage(NewLearningUnitPage):
    code_dedie_au_partim = InputField(By.ID, "id_acronym_2")
    save_button = ButtonField(By.XPATH,
                              '//*[@id="LearningUnitYearForm"]/div[1]/div/div/button')


class DescriptionPage(pypom.Page):
    methode_denseignement = CkeditorField(By.CLASS_NAME, 'cke_wysiwyg_frame')

    add_button = ButtonField(By.XPATH, '//*[@id="pedagogy"]/div[2]/div[2]/div/a')
    save_button = Link('DescriptionPage', By.XPATH, '//*[@id="form-modal-ajax-content"]/form/div[3]/button[1]', 2)

    intitule = InputField(By.ID, 'id_title')
    support_obligatoire = RadioField(By.ID, 'id_mandatory')

    def find_edit_button(self, _):
        return self.find_element(By.XPATH, '//*[@id="pedagogy"]/table[1]/tbody/tr[2]/td[2]/a')



class LearningUnitPage(pypom.Page):
    actions = ButtonField(By.ID, "dLabel")
    edit_button = ButtonField(By.CSS_SELECTOR, "#link_edit_lu > a")
    new_partim = Link(NewPartimPage, By.ID, "new_partim")
    go_to_full = ButtonField(By.ID, "full_acronym")

    tab_training = Link(LearningUnitTrainingPage, By.ID, "training_link")
    tab_attribution = Link(LearningUnitAttributionPage, By.ID, "attributions_link")
    tab_description = Link(DescriptionPage, By.ID, "description_link")

    def success_messages(self):
        success_panel = self.find_element(By.ID, "pnl_succes_messages")
        return success_panel.text

    def is_li_edit_link_disabled(self):
        return "disabled" in self.find_element(By.ID, "link_edit_lu").get_attribute("class")

    @property
    def loaded(self) -> bool:
        return bool("active" in self.find_element(By.XPATH, '//*[@id="main"]/ol/li[4]').get_attribute('class'))


class LearningUnitEditPage(pypom.Page):
    actif = Checkbox(By.ID, "id_status")
    periodicite = SelectField(By.ID, "id_periodicity")
    credits = InputField(By.ID, "id_credits")
    volume_q1_pour_la_partie_magistrale = InputField(By.ID, "id_component-0-hourly_volume_partial_q1")
    volume_q1_pour_la_partie_pratique = InputField(By.ID, "id_component-1-hourly_volume_partial_q1")
    volume_q2_pour_la_partie_magistrale = InputField(By.ID, "id_component-0-hourly_volume_partial_q2")
    volume_q2_pour_la_partie_pratique = InputField(By.ID, "id_component-1-hourly_volume_partial_q2")
    quadrimestre = SelectField(By.ID, "id_quadrimester")
    session_derogation = SelectField(By.ID, "id_session")

    save_button = ButtonField(By.CSS_SELECTOR,
                              "#main > div.panel.panel-default > div.panel-heading > div > div > button")

    no_postponement = Link(LearningUnitPage, By.ID, "btn_without_postponement")
    with_postponement = Link(LearningUnitPage, By.ID, "btn_with_postponement")


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

    actions = ButtonField(By.XPATH, '//*[@id="main"]/div[3]/div/div[2]/div/button')
    new_luy = Link(NewLearningUnitPage, By.ID, 'lnk_learning_unit_create')

    def count_result(self):
        text = self.find_element(By.CSS_SELECTOR, "#main > div.panel.panel-default > div > strong").text
        return text.split()[0]

    def find_acronym_in_table(self, row: int = 1, col: int = 2):
        selector = '// *[ @ id = "table_learning_units"] / tbody / tr[{}] / td[{}] / a'.format(row, col)
        return self.find_element(By.XPATH, selector).text
