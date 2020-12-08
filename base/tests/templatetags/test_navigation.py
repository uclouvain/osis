############################################################################
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
############################################################################
import urllib
from unittest import mock

from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from base.forms.learning_unit.search.simple import LearningUnitFilter
from base.models.learning_unit_year import LearningUnitYear
from base.templatetags import navigation
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.user import UserFactory
from base.utils.cache import SearchParametersCache
from base.views.learning_units.search.common import SearchTypes
from education_group.models.group_year import GroupYear
from education_group.tests.factories.group_year import GroupYearFactory
from program_management.tests.factories.education_group_version import EducationGroupVersionFactory
from program_management.tests.factories.element import ElementFactory


class TestNavigationMixin:
    search_type = "DEFINE"

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.elements = cls.generate_elements()
        cls.user = UserFactory()

    @classmethod
    def generate_elements(cls):
        raise NotImplementedError

    @property
    def url_name(self):
        raise NotImplementedError()

    def _get_element_url(self, query_parameters: QueryDict, index):
        raise NotImplementedError()

    def navigation_function(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def elements_sorted_by_acronym(self):
        return sorted(self.elements, key=lambda obj: obj.acronym)

    def setUp(self):
        self.query_parameters = QueryDict(mutable=True)
        self.query_parameters["search_query"] = urllib.parse.quote_plus(
            'academic_year={academic_year}&ordering=acronym'.format(
                academic_year=self.academic_year.id
            )
        )
        parameters = QueryDict('academic_year={academic_year}&ordering=acronym'.format(
            academic_year=self.academic_year.id
        ))
        self.cache = SearchParametersCache(self.user, self.search_type)
        self.cache.set_cached_data(parameters)

    def tearDown(self):
        self.cache.clear()

    def assertNavigationContextEquals(self, expected_context, index, group=False):
        if group:
            context = self.navigation_function(
                self.user,
                self.elements_sorted_by_acronym[index],
                self.url_name,
                None
            )
        else:
            context = self.navigation_function(
                self.user,
                self.elements_sorted_by_acronym[index],
                self.url_name
            )
        self.assertEqual(context["current_element"], expected_context["current_element"])
        self.assertEqual(context["next_element_title"], expected_context["next_element_title"])
        self.assertEqual(context["previous_element_title"], expected_context["previous_element_title"])
        self.assertURLEqual(context["next_url"], expected_context["next_url"])
        self.assertURLEqual(context["previous_url"], expected_context["previous_url"])


class TestNavigationLearningUnitYear(TestNavigationMixin, TestCase):
    search_type = LearningUnitYear.__name__

    @classmethod
    def generate_elements(cls):
        return LearningUnitYearFactory.create_batch(5, academic_year=cls.academic_year)

    @property
    def url_name(self):
        return 'learning_unit'

    def navigation_function(self, *args, **kwargs):
        return navigation.navigation_learning_unit(*args, **kwargs)

    def _get_element_url(self, query_parameters: QueryDict, index):
        next_element = self.elements_sorted_by_acronym[index]

        return reverse(self.url_name, args=[next_element.acronym, next_element.academic_year.year])

    def test_filter_called_depending_on_search_type(self):
        parameters = {
            "academic_year": "self.academic_year.id",
            "ordering": "acronym",
            "search_type": SearchTypes.EXTERNAL_SEARCH.value
        }
        self.cache.set_cached_data(parameters)

        self.filter_form_patcher = mock.patch("base.templatetags.navigation._get_learning_unit_filter_class",
                                              return_value=LearningUnitFilter)
        self.mocked_filter_form = self.filter_form_patcher.start()

        self.navigation_function(
            self.user,
            self.elements_sorted_by_acronym[0],
            self.url_name,
        )

        self.assertTrue(self.mocked_filter_form.called)

        self.filter_form_patcher.stop()

    def test_navigation_when_no_search_query(self):
        self.cache.clear()

        context = self.navigation_function(
            self.user,
            self.elements_sorted_by_acronym[0],
            self.url_name,
        )

        expected_context = {"current_element": self.elements_sorted_by_acronym[0]}
        self.assertDictEqual(context, expected_context)

    def test_first_element_should_not_have_previous_element(self):
        first_element_index = 0
        expected_context = {
            "current_element": self.elements_sorted_by_acronym[first_element_index],
            "next_element_title": self.elements_sorted_by_acronym[first_element_index + 1].acronym,
            "next_url": self._get_element_url(self.query_parameters, first_element_index + 1),
            "previous_element_title": None,
            "previous_url": None,
        }
        self.assertNavigationContextEquals(expected_context, first_element_index)

    def test_last_element_should_not_have_next_element(self):
        last_element_index = len(self.elements_sorted_by_acronym) - 1
        expected_context = {
            "current_element": self.elements_sorted_by_acronym[last_element_index],
            "next_element_title": None,
            "next_url": None,
            "previous_element_title": self.elements_sorted_by_acronym[last_element_index - 1].acronym,
            "previous_url": self._get_element_url(self.query_parameters, last_element_index - 1),
        }
        self.assertNavigationContextEquals(expected_context, last_element_index)

    def test_inner_element_should_have_previous_and_next_element(self):
        inner_element_index = 2
        expected_context = {
            "current_element": self.elements_sorted_by_acronym[inner_element_index],
            "next_element_title": self.elements_sorted_by_acronym[inner_element_index + 1].acronym,
            "next_url": self._get_element_url(self.query_parameters, inner_element_index + 1),
            "previous_element_title": self.elements_sorted_by_acronym[inner_element_index - 1].acronym,
            "previous_url": self._get_element_url(self.query_parameters, inner_element_index - 1),
        }
        self.assertNavigationContextEquals(expected_context, inner_element_index)


class TestNavigationGroupYear(TestNavigationMixin, TestCase):
    search_type = GroupYear.__name__
    current_version_value = 9  # TODO : Devrait être un programTreeVersion

    @classmethod
    def generate_elements(cls):
        group_years = GroupYearFactory.create_batch(5, academic_year=cls.academic_year)
        for group_year in group_years:
            ElementFactory(group_year=group_year)
        [EducationGroupVersionFactory(root_group=group) for group in group_years]
        return group_years

    def _get_element_url(self, query_parameters: QueryDict, index):
        next_element = self.elements_sorted_by_acronym[index]
        return reverse(self.url_name, args=[next_element.academic_year.year, next_element.partial_acronym])

    @property
    def url_name(self):
        return 'training_identification'

    def navigation_function(self, *args, **kwargs):
        return navigation.navigation_group(*args, **kwargs)

    def test_navigation_when_no_search_query(self):
        self.cache.clear()

        context = self.navigation_function(
            self.user,
            self.elements_sorted_by_acronym[0],
            self.url_name,
            None
        )

        expected_context = {"current_element": self.elements_sorted_by_acronym[0]}
        self.assertDictEqual(context, expected_context)

    def test_first_element_should_not_have_previous_element(self):
        first_element_index = 0
        expected_context = {
            "current_element": self.elements_sorted_by_acronym[first_element_index],
            "next_element_title": "{}{}".format(
                self.elements_sorted_by_acronym[first_element_index + 1].acronym,
                "[{}]".format(
                    self.elements_sorted_by_acronym[first_element_index + 1].educationgroupversion.version_name)
                if self.elements_sorted_by_acronym[first_element_index + 1].educationgroupversion.version_name else ''
            ),
            "next_url": self._get_element_url(
                self.query_parameters,
                first_element_index + 1
            ) + '?path=' + str(self.elements_sorted_by_acronym[first_element_index + 1].element.id),
            "previous_element_title": None,
            "previous_url": None,
        }
        self.assertNavigationContextEquals(expected_context, first_element_index, True)

    def test_last_element_should_not_have_next_element(self):
        last_element_index = len(self.elements_sorted_by_acronym) - 1
        expected_context = {
            "current_element": self.elements_sorted_by_acronym[last_element_index],
            "next_element_title": None,
            "next_url": None,
            "previous_element_title": "{}{}".format(
                self.elements_sorted_by_acronym[last_element_index - 1].acronym,
                "[{}]".format(
                    self.elements_sorted_by_acronym[last_element_index - 1].educationgroupversion.version_name) if
                self.elements_sorted_by_acronym[last_element_index - 1].educationgroupversion.version_name else ''
            ),
            "previous_url": self._get_element_url(
                self.query_parameters,
                last_element_index - 1
            ) + '?path=' + str(self.elements_sorted_by_acronym[last_element_index - 1].element.id),
            "current_version": None
        }
        self.assertNavigationContextEquals(expected_context, last_element_index, True)

    def test_inner_element_should_have_previous_and_next_element(self):
        inner_element_index = 2

        expected_context = {
            "current_element": self.elements_sorted_by_acronym[inner_element_index],
            "next_element_title": "{}{}".format(self.elements_sorted_by_acronym[inner_element_index + 1].acronym,
                                                "[{}]".format(
                                                    self.elements_sorted_by_acronym[
                                                        inner_element_index + 1].educationgroupversion.version_name) if
                                                self.elements_sorted_by_acronym[
                                                    inner_element_index + 1].educationgroupversion.version_name else ''
                                                ),
            "next_url": self._get_element_url(
                self.query_parameters,
                inner_element_index + 1
            ) + '?path=' + str(self.elements_sorted_by_acronym[inner_element_index + 1].element.id),
            "previous_element_title": "{}{}".format(
                self.elements_sorted_by_acronym[inner_element_index - 1].acronym,
                "[{}]".format(
                    self.elements_sorted_by_acronym[inner_element_index - 1].educationgroupversion.version_name) if
                self.elements_sorted_by_acronym[inner_element_index - 1].educationgroupversion.version_name else ''),
            "previous_url": self._get_element_url(
                self.query_parameters,
                inner_element_index - 1
            ) + '?path=' + str(self.elements_sorted_by_acronym[inner_element_index - 1].element.id),
        }
        self.assertNavigationContextEquals(expected_context, inner_element_index, True)

    def test_navigation_with_version(self):
        self.cache.clear()

        context = self.navigation_function(
            self.user,
            self.elements_sorted_by_acronym[0],
            self.url_name,
            self.current_version_value
        )

        self.assertEqual(context['current_version'], self.current_version_value)
