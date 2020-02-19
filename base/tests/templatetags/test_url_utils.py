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
from django.test import SimpleTestCase, RequestFactory

from base.templatetags import url_utils


class TestUrlParameters(SimpleTestCase):
    def test_no_arguments_should_return_empty_string(self):
        result = url_utils.url_params({})
        expected_result = ""
        self.assertEqual(result, expected_result)

    def test_should_return_query_string_containing_arguments_value(self):
        result = url_utils.url_params({}, key1="value1", key2="value2")
        expected_result = "?key1=value1&key2=value2"
        self.assertURLEqual(result, expected_result)

    def test_should_exclude_none_value(self):
        result = url_utils.url_params({}, key1="value1", key2="value2", key3=None)
        expected_result = "?key1=value1&key2=value2"
        self.assertURLEqual(result, expected_result)

    def test_should_convert_values_to_str(self):
        result = url_utils.url_params({}, key1=1, key2=True)
        expected_result = "?key1=1&key2=True"
        self.assertURLEqual(result, expected_result)

    def test_should_keep_existing_query_parameters_from_request(self):
        request = RequestFactory().get("/path/", data={"key2": "value_to_update", "key3": "value3"})
        result = url_utils.url_params({"request": request}, key1="value1", key2="value2")
        expected_result = "?key1=value1&key2=value2&key3=value3"
        self.assertURLEqual(result, expected_result)
