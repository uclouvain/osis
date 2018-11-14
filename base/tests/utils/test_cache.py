##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.user import UserFactory
from base.utils.cache import cache, clear_cached_filter, _get_filter_key, _restore_filter_from_cache, \
    _save_filter_to_cache, get_filter_value_from_cache


class TestClearCachedFilter(TestCase):
    def setUp(self):
        cache.clear()
        self.url_cached = 'dummy_url'
        self.user = UserFactory()

        request_factory = RequestFactory()
        self.request = request_factory.post(reverse("clear_filter"), data={'current_url': self.url_cached})
        self.request.user = self.user

    def tearDown(self):
        cache.clear()

    def test_clear_cached_filter(self):
        key = _get_filter_key(self.user, self.url_cached)
        filter_to_cached = {'filter_a': 'ABCD', 'filter_b': 'CDEF'}
        cache.set(key, filter_to_cached)
        # Check that cache is set
        self.assertDictEqual(cache.get(key), filter_to_cached)

        # Clear fitler cache
        clear_cached_filter(self.request)
        self.assertIsNone(cache.get(key))


class TestSaveAndRestoreFilterFromCache(TestCase):
    def setUp(self):
        cache.clear()
        self.data_cached = {
            "name": "Axandre",
            "city": "City25",
        }
        self.user = UserFactory()

        request_factory = RequestFactory()
        self.request_without_get_data = request_factory.get("www.url.com")
        self.request_without_get_data.user = self.user

        self.request = request_factory.get("www.url.com", data=self.data_cached)
        self.request.user = self.user

    def tearDown(self):
        cache.clear()

    def test_use_default_values_if_nothing_in_cache(self):
        default_values = {
            "name": "A name",
            "city": "A city",
        }
        _restore_filter_from_cache(self.request_without_get_data, **default_values)
        self.assertEqual(self.request_without_get_data.GET.dict(),
                         default_values)

    def test_use_cache_values_and_not_default_ones_if_values_in_cache(self):
        _save_filter_to_cache(self.request)
        default_values = {
            "name": "A name",
            "city": "A city",
        }
        _restore_filter_from_cache(self.request, **default_values)
        self.assertNotEqual(self.request.GET.dict(),
                            default_values)
        self.assertEqual(self.request.GET.dict(),
                         self.data_cached)


class TestGetFilterValueFromCache(TestCase):
    def setUp(self):
        self.url_cached = 'dummy_url'
        self.user = UserFactory()
        key = _get_filter_key(self.user, self.url_cached)

        filter_to_cached = {'filter_a': 'ABCD', 'filter_b': 'CDEF'}
        cache.clear()
        cache.set(key, filter_to_cached)

    def tearDown(self):
        cache.clear()

    def test_get_filter_value_from_cache_case_success(self):
        filter_values = get_filter_value_from_cache(self.user, self.url_cached, 'filter_a')
        expected_value = 'ABCD'
        self.assertEqual(filter_values, expected_value)

    def test_get_filter_value_from_cache_case_no_filter_key_found(self):
        self.assertIsNone(get_filter_value_from_cache(self.user, self.url_cached, 'filter_c'))

    def test_get_filter_value_from_cache_case_no_cache_set(self):
        cache.clear()
        self.assertIsNone(get_filter_value_from_cache(self.user, self.url_cached, 'filter_c'))
