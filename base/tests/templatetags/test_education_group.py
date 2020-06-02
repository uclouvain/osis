##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from waffle.testutils import override_switch

from base.templatetags.education_group import link_pdf_content_education_group, dl_with_parent, \
    have_only_access_to_certificate_aims
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import TrainingFactory, EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from education_group.tests.factories.auth.central_manager import CentralManagerFactory

DELETE_MSG = _("delete education group")
PERMISSION_DENIED_MSG = _("This education group is not editable during this period.")
UNAUTHORIZED_TYPE_MSG = "No type of %(child_category)s can be created as child of %(category)s of type %(type)s"

CUSTOM_LI_TEMPLATE = """
    <li {li_attributes}>
        <a {a_attributes} data-toggle="tooltip">{text}</a>
    </li>
"""


class TestEducationGroupAsCentralManagerTag(TestCase):
    """ This class will test the tag as central manager """
    @classmethod
    def setUpTestData(cls):
        academic_year = AcademicYearFactory(year=2020)
        cls.education_group_year = TrainingFactory(academic_year=academic_year)
        cls.person = PersonFactory()
        CentralManagerFactory(person=cls.person, entity=cls.education_group_year.management_entity)

        cls.url = reverse('delete_education_group', args=[cls.education_group_year.id, cls.education_group_year.id])

        cls.request = RequestFactory().get("")

    def setUp(self):
        self.client.force_login(user=self.person.user)
        self.context = {
            "person": self.person,
            "education_group_year": self.education_group_year,
            "request": self.request,
            "root": self.education_group_year,
        }

    @override_switch('education_group_year_generate_pdf', active=True)
    def test_tag_link_pdf_content_education_group_not_permitted(self):
        result = link_pdf_content_education_group(self.context)
        self.assertEqual(
            result,
            {
                'url': {
                    'person': self.person,
                    'education_group_year': self.education_group_year,
                    'request': self.request,
                    'root': self.education_group_year
                },
                'text': 'Générer le pdf',
                'class_li': '',
                'title': 'Générer le pdf',
                'id_li': 'btn_operation_pdf_content',
                'load_modal': True
            }
        )

    @override_switch('education_group_year_generate_pdf', active=False)
    def test_tag_link_pdf_content_education_group_not_permitted_with_sample_deactivated(self):
        result = link_pdf_content_education_group(self.context)
        self.assertEqual(
            result,
            {
                'url': '#',
                'text': 'Générer le pdf',
                'class_li': 'disabled',
                'title': 'Générer le PDF n\'est pas disponible. Veuillez utiliser EPC.',
                'id_li': 'btn_operation_pdf_content',
                'load_modal': False
            }
        )


class TestEducationGroupDlWithParent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = EducationGroupYearFactory()

    def setUp(self):
        self.education_group_year = EducationGroupYearFactory()
        self.context = {
            'parent': self.parent,
            'education_group_year': self.education_group_year,
        }

    def test_dl_value_in_education_group(self):
        response = dl_with_parent(self.context, "acronym")
        self.assertEqual(response["value"], self.education_group_year.acronym)
        self.assertEqual(response["label"], _("Acronym/Short title"))
        self.assertEqual(response["parent_value"], None)

    def test_dl_value_in_parent(self):
        self.education_group_year.acronym = ""
        response = dl_with_parent(self.context, "acronym")
        self.assertEqual(response["value"], "")
        self.assertEqual(response["label"], _("Acronym/Short title"))
        self.assertEqual(response["parent_value"], self.parent.acronym)

    def test_dl_default_value(self):
        self.education_group_year.acronym = ""
        self.parent.acronym = ""
        response = dl_with_parent(self.context, "acronym", default_value="avada kedavra")

        self.assertEqual(response["value"], "")
        self.assertEqual(response["label"], _("Acronym/Short title"))
        self.assertEqual(response["parent_value"], "")
        self.assertEqual(response["default_value"], "avada kedavra")

    def test_dl_with_bool(self):
        self.education_group_year.partial_deliberation = False
        response = dl_with_parent(self.context, "partial_deliberation")
        self.assertEqual(response["value"], "no")
        self.assertEqual(response["parent_value"], None)

        self.education_group_year.partial_deliberation = True
        response = dl_with_parent(self.context, "partial_deliberation")
        self.assertEqual(response["value"], "yes")
        self.assertEqual(response["parent_value"], None)

        self.education_group_year.partial_deliberation = None
        self.parent.partial_deliberation = True
        response = dl_with_parent(self.context, "partial_deliberation")
        self.assertEqual(response["value"], None)
        self.assertEqual(response["parent_value"], "yes")

    def test_dl_invalid_key(self):
        self.education_group_year.partial_deliberation = False
        with self.assertRaises(FieldDoesNotExist):
            dl_with_parent(self.context, "not_a_real_attr")


# TODO: Remove when migration of program_manager done
class TestHaveOnlyAccessCertificateAims(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group_year = EducationGroupYearFactory()

    def setUp(self):
        self.person = PersonFactory()

    def test_have_only_access_certificates_aims_case_no_role(self):
        self.assertFalse(
            have_only_access_to_certificate_aims(self.person.user, self.education_group_year)
        )

    def test_have_only_access_certificates_aims_case_only_program_manager(self):
        ProgramManagerFactory(education_group=self.education_group_year.education_group, person=self.person)
        self.assertTrue(
            have_only_access_to_certificate_aims(self.person.user, self.education_group_year)
        )

    def test_have_only_access_certificates_aims_case_program_manager_and_central_manager(self):
        ProgramManagerFactory(education_group=self.education_group_year.education_group, person=self.person)
        CentralManagerFactory(person=self.person)
        self.assertFalse(
            have_only_access_to_certificate_aims(self.person.user, self.education_group_year)
        )
