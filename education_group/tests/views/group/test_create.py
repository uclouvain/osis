from collections import defaultdict
from typing import List
from unittest import mock

from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.test import TestCase
from django.urls import reverse, exceptions
from django.utils.translation import gettext_lazy as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import GroupEducationGroupTypeFactory
from base.tests.factories.person import PersonFactory
from education_group.ddd.domain.group import GroupIdentity
from education_group.forms.group import GroupForm
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.factories.group_year import GroupYearFactory


class TestCreateGroupGetMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.type = GroupEducationGroupTypeFactory()

        cls.central_manager = CentralManagerFactory()
        cls.parent = GroupYearFactory(
            partial_acronym="LDROI1200",
            academic_year=cls.academic_year,
            management_entity=cls.central_manager.entity
        )
        cls.url = reverse('group_create', kwargs={'type': cls.type.name}) +\
            "?attach_to={parent_code}_{parent_year}".format(
                parent_code=cls.parent.partial_acronym,
                parent_year=cls.parent.academic_year.year
            )

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_when_user_has_no_permission(self):
        a_person_without_permission = PersonFactory()
        self.client.force_login(a_person_without_permission.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_when_attach_to_querystring_arg_not_provided(self):
        url_without_attach_to = reverse('group_create', kwargs={'type': self.type.name})
        response = self.client.get(url_without_attach_to)
        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

    def test_when_type_in_url_is_not_supported(self):
        with self.assertRaises(exceptions.NoReverseMatch):
            reverse('group_create', kwargs={'type': 'dummy-type'})

    def test_assert_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "education_group_app/group/upsert/create.html")

    def test_assert_context(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['group_form'], GroupForm)
        self.assertIsInstance(response.context['tabs'], List)

    def test_assert_contains_only_identification_tabs(self):
        response = self.client.get(self.url)

        self.assertListEqual(
            response.context['tabs'],
            [{
                "text": _("Identification"),
                "active": True,
                "display": True,
                "include_html": "education_group_app/group/upsert/identification_form.html"
            }]
        )


class TestCreateGroupPostMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.type = GroupEducationGroupTypeFactory()

        cls.central_manager = CentralManagerFactory()
        cls.parent = GroupYearFactory(
            partial_acronym="LDROI1200",
            academic_year=cls.academic_year,
            management_entity=cls.central_manager.entity
        )
        cls.url = reverse('group_create', kwargs={'type': cls.type.name}) + \
            "?attach_to={parent_code}_{parent_year}".format(
              parent_code=cls.parent.partial_acronym,
              parent_year=cls.parent.academic_year.year
            )

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_case_when_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url, data={})
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_when_user_has_no_permission(self):
        a_person_without_permission = PersonFactory()
        self.client.force_login(a_person_without_permission.user)

        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_when_attach_to_querystring_arg_not_provided(self):
        url_without_attach_to = reverse('group_create', kwargs={'type': self.type.name})
        response = self.client.post(url_without_attach_to, data={})
        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

    def test_post_missing_data_assert_template_and_context(self):
        with mock.patch('education_group.views.group.create.GroupForm.is_valid', return_value=False):
            response = self.client.post(self.url, data={})
            self.assertEqual(response.status_code, HttpResponse.status_code)
            self.assertTemplateUsed(response, "education_group_app/group/upsert/create.html")

            self.assertIsInstance(response.context['group_form'], GroupForm)
            self.assertIsInstance(response.context['tabs'], List)

    @mock.patch('education_group.views.group.create.group_service.create_group')
    @mock.patch('education_group.views.group.create.GroupForm', create_autospec=True)
    def test_post_assert_create_service_called(self, mock_group_form, mock_service_create_group):
        mock_group_form.is_valid.return_value = True
        mock_group_form.cleaned_data.return_value = defaultdict()

        mock_service_create_group.return_value = GroupIdentity(code="LTRONC1000", year=2018)

        self.client.post(self.url)
        mock_service_create_group.assert_called_once()
