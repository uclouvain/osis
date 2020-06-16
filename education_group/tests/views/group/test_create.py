from typing import List

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.test import TestCase
from django.urls import reverse, exceptions
from django.utils.translation import gettext_lazy as _

from base.models.enums import organization_type
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.education_group_type import GroupEducationGroupTypeFactory
from base.tests.factories.entity_version import MainEntityVersionFactory
from base.tests.factories.person import PersonFactory
from education_group.forms.group import GroupForm
from education_group.tests.factories.auth.central_manager import CentralManagerFactory
from education_group.tests.factories.group_year import GroupYearFactory


class TestCreateGroupGetMethod(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.type = GroupEducationGroupTypeFactory()
        cls.entity_version = MainEntityVersionFactory(acronym='DRT')
        cls.campus = CampusFactory(organization__type=organization_type.MAIN)

        cls.parent = GroupYearFactory(
            partial_acronym="LDROI1200",
            academic_year=cls.academic_year,
            management_entity=cls.entity_version.entity
        )
        cls.central_manager = CentralManagerFactory(entity=cls.entity_version.entity)
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
        url = reverse('group_create', kwargs={'type': self.type.name})
        response = self.client.get(url)
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
