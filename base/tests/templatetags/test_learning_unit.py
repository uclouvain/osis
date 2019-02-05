##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from collections import OrderedDict

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from base.templatetags.learning_unit import get_difference_css, has_proposal, get_previous_acronym, value_label, \
    DIFFERENCE_CSS, _volume_format, get_component_volume_css, dl_component_tooltip
from base.tests.factories.learning_unit_year import LearningUnitYearFactory, create_learning_units_year
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.models.proposal_learning_unit import ProposalLearningUnit
from django.utils.safestring import mark_safe
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.templatetags.learning_unit import th_tooltip, CSS_PROPOSAL_VALUE, LABEL_VALUE_BEFORE_PROPOSAL
from reference.tests.factories.language import LanguageFactory
from base.models.enums.learning_unit_year_periodicity import PERIODICITY_TYPES, ANNUAL
from base.tests.factories.learning_component_year import LearningComponentYearFactory

ENTITY_ACRONYM = "AGRO"
VOLUME = 20
OTHER_VOLUME = 25


class LearningUnitTagTest(TestCase):

    def setUp(self):
        self.entity_vers = EntityVersionFactory(acronym=ENTITY_ACRONYM)

    def test_get_difference_css(self):
        key_parameter_1 = 'parameter1'
        tooltip_parameter1 = 'tooltip1'

        differences = {key_parameter_1: tooltip_parameter1,
                       'parameter2': 'tooltip2'}

        self.assertEqual(get_difference_css(differences, key_parameter_1),
                         " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                                   tooltip_parameter1,
                                                                                   CSS_PROPOSAL_VALUE))

    def test_get_no_differences_css(self):
        differences = {'parameter1': 'tooltip1'}
        self.assertIsNone(get_difference_css(differences, 'parameter_10'))

    def test_has_proposal(self):
        luy = LearningUnitYearFactory()
        self.assertFalse(has_proposal(luy))
        ProposalLearningUnitFactory(learning_unit_year=luy)
        self.assertTrue(has_proposal(luy))

    def test_previous_acronym(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2013, 2016, learning_unit)

        lu_yr_1 = dict_learning_unit_year.get(2013)
        lu_yr_1.acronym = "LBIR1212"
        lu_yr_1.save()

        lu_yr_2 = dict_learning_unit_year.get(2014)
        lu_yr_2.acronym = "LBIR1213"
        lu_yr_2.save()

        lu_yr_3 = dict_learning_unit_year.get(2015)
        lu_yr_3.acronym = "LBIR1214"
        lu_yr_3.save()

        self.assertEqual(get_previous_acronym(lu_yr_3), 'LBIR1213')
        self.assertEqual(get_previous_acronym(lu_yr_2), 'LBIR1212')
        self.assertIsNone(get_previous_acronym(lu_yr_1))

    def test_previous_acronym_with_acronym(self):
        learning_unit = LearningUnitFactory()
        dict_learning_unit_year = create_learning_units_year(2013, 2013, learning_unit)

        l_unit = dict_learning_unit_year.get(2013)
        initial_acronym = l_unit.acronym
        new_acronym = "{}9".format(l_unit.acronym)
        l_unit.acronym = new_acronym
        l_unit.save()

        ProposalLearningUnitFactory(learning_unit_year=l_unit,
                                    initial_data={'learning_unit_year': {'acronym': initial_acronym}})

        self.assertEqual(get_previous_acronym(l_unit), initial_acronym)

    def test_value_label_equal_values(self):
        data = self.get_dict_data()
        key = 'REQUIREMENT_ENTITY'
        sub_key = 'next'
        value_to_comp = 'current'

        self.assertCountEqual(value_label(data, key, sub_key=sub_key, key_comp=value_to_comp),
                              mark_safe("{}".format('DEXT')))

    def get_dict_data(self):
        return OrderedDict([('REQUIREMENT_ENTITY', {'current': 'DEXT', 'next': 'DEXT', 'prev': None}),
                            ("campus", {'current': 'campus 1', 'next': 'campus 2', 'prev': 'campus1'})
                            ])

    def test_value_label_different_values(self):
        data = self.get_dict_data()
        key = 'campus'
        sub_key = 'next'
        value_to_comp = 'current'

        self.assertCountEqual(value_label(data, key, sub_key=sub_key, key_comp=value_to_comp),
                              mark_safe("<label {}>{}</label>".format(DIFFERENCE_CSS, 'campus 2')))

    def test_numeric_format(self):
        self.assertEqual(_volume_format(None), '')
        self.assertEqual(_volume_format(20), 20)
        self.assertEqual(_volume_format(20.50), '20.5')

    def test_get_component_volume_css(self):
        values = {'param1': 20, 'param2': 'test2'}
        self.assertEqual(get_component_volume_css(values, 'param1', None, 25), mark_safe(
            " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                      20,
                                                                      CSS_PROPOSAL_VALUE)))

    def test_th_tooltip(self):
        differences = {'REQUIREMENT_ENTITY': self.entity_vers.entity.id}
        context = {'differences': differences}

        self.assertEqual(
            th_tooltip(context=context, key='REQUIREMENT_ENTITY', value=self.entity_vers.entity),
            "<span  data-toggle=tooltip title='{} : {}' class='{}' >{}</span>".format(
                LABEL_VALUE_BEFORE_PROPOSAL, ENTITY_ACRONYM, CSS_PROPOSAL_VALUE, ENTITY_ACRONYM)
        )

    def test_th_tooltip_no_css(self):
        self.assertEqual(
            th_tooltip(context={'differences': {}}, key='REQUIREMENT_ENTITY', value=self.entity_vers.entity),
            "<span >{}</span>".format(ENTITY_ACRONYM)
        )

    def test_get_differences_css_for_entity(self):
        differences = {'REQUIREMENT_ENTITY': self.entity_vers.entity.id}

        self.assertEqual(get_difference_css(differences, 'REQUIREMENT_ENTITY'), mark_safe(
            " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                      ENTITY_ACRONYM,
                                                                      CSS_PROPOSAL_VALUE)))

    def test_get_difference_css_language(self):

        differences = {'language': LanguageFactory(name="French").id}

        self.assertEqual(get_difference_css(differences, 'language'), mark_safe(
            " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                      "French",
                                                                      CSS_PROPOSAL_VALUE)))

    def test_get_difference_css_luy(self):
        luy = LearningUnitYearFactory(periodicity=ANNUAL, status=True)

        differences = {'periodicity': luy.periodicity, 'status': True}

        self.assertEqual(get_difference_css(differences, 'periodicity'), mark_safe(
            " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                      _(dict(PERIODICITY_TYPES)["ANNUAL"]),
                                                                      CSS_PROPOSAL_VALUE)))
        self.assertEqual(get_difference_css(differences, 'status'), mark_safe(
            " data-toggle=tooltip title='{} : {}' class='{}' ".format(LABEL_VALUE_BEFORE_PROPOSAL,
                                                                      _("Active"),
                                                                      CSS_PROPOSAL_VALUE)))

    def test_dl_component_tooltip(self):
        self.assertEqual(dl_component_tooltip({}, "VOLUME_Q1", value=VOLUME), VOLUME)
        self.assertEqual(dl_component_tooltip({'components_initial_data': {}}, "VOLUME_Q1", value=VOLUME), VOLUME)
        lcy = LearningComponentYearFactory(hourly_volume_partial_q1=OTHER_VOLUME)

        context = {
            'components_initial_data': {
                'components': [
                    {
                        'learning_component_year': {'id': lcy.id,
                                                    'hourly_volume_partial_q1': lcy.hourly_volume_partial_q1},
                        'volumes': {'VOLUME_Q1': OTHER_VOLUME}}
                    ,
                ]
            }
        }
        expected_html = "<dl><dd  data-toggle=tooltip title='{} : {}' class='{}'  id='id_volume_q1'><p style='' " \
                        "title=''>{}</p></dd></dl>". \
            format(LABEL_VALUE_BEFORE_PROPOSAL, OTHER_VOLUME, CSS_PROPOSAL_VALUE, VOLUME)
        self.assertEqual(
            dl_component_tooltip(context, "VOLUME_Q1", value=VOLUME, id=lcy.id),
            expected_html)
