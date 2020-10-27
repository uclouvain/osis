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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mock import patch

from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.proposal_state import ProposalState
from base.templatetags.learning_unit_li import is_valid_proposal, MSG_IS_NOT_A_PROPOSAL, \
    MSG_PROPOSAL_NOT_ON_CURRENT_LU, DISABLED, li_cancel_proposal, li_edit_proposal, li_consolidate_proposal, \
    li_delete_all_lu
from base.tests.factories import academic_calendar as acad_calendar_factory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.entity import EntityWithVersionFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from learning_unit.tests.factories.central_manager import CentralManagerFactory
from learning_unit.tests.factories.faculty_manager import FacultyManagerFactory

ID_LINK_EDIT_LU = "link_edit_lu"
ID_LINK_EDIT_DATE_LU = "link_edit_date_lu"


@override_settings(YEAR_LIMIT_LUE_MODIFICATION=2018)
class LearningUnitTagLiEditTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = CentralManagerFactory(entity=EntityWithVersionFactory(), with_child=True)
        cls.person = cls.manager.person

        cls.previous_learning_unit = LearningUnitFactory()
        cls.current_academic_year = create_current_academic_year()
        cls.next_academic_yr = AcademicYearFactory(year=cls.current_academic_year.year + 1)

        anac_2 = AcademicYearFactory(year=cls.current_academic_year.year + 2)
        anac_3 = AcademicYearFactory(year=cls.current_academic_year.year + 3)
        anac_4 = AcademicYearFactory(year=cls.current_academic_year.year + 4)
        cls.later_academic_year = AcademicYearFactory(year=cls.current_academic_year.year + 5)

        academic_years = [
            cls.current_academic_year, cls.next_academic_yr, anac_2, anac_3, anac_4, cls.later_academic_year
        ]
        acad_calendar_factory.generate_creation_or_end_date_proposal_calendars(academic_years)
        acad_calendar_factory.generate_modification_transformation_proposal_calendars(academic_years)
        acad_calendar_factory.generate_learning_unit_edition_calendars(academic_years)

        cls.requirement_entity = cls.manager.entity

        cls.lcy = LearningContainerYearFactory(
            academic_year=cls.next_academic_yr,
            container_type=learning_container_year_types.COURSE,
            requirement_entity=cls.requirement_entity
        )
        cls.request = RequestFactory().get("")

    def setUp(self):
        self.learning_unit = LearningUnitFactory()
        self.previous_learning_unit = LearningUnitFactory()
        self.current_academic_year = create_current_academic_year()
        self.previous_academic_year = AcademicYearFactory(year=settings.YEAR_LIMIT_LUE_MODIFICATION-1)
        self.next_academic_year = AcademicYearFactory(year=settings.YEAR_LIMIT_LUE_MODIFICATION + 1)

        self.learning_unit_year = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=self.learning_unit,
            learning_container_year=self.lcy
        )
        self.learning_unit_year.initial_data = {"learning_container_year": self.lcy}
        self.previous_learning_unit_year = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            learning_unit=self.learning_unit,
            learning_container_year__requirement_entity=self.manager.entity
        )
        self.previous_luy_2 = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=self.previous_learning_unit,
            learning_container_year=LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                                                 container_type=learning_container_year_types.COURSE)
        )

        self.client.force_login(user=self.person.user)

        self.proposal = ProposalLearningUnitFactory(
            learning_unit_year=self.learning_unit_year,
            learning_unit_year__learning_container_year=self.lcy,
            initial_data={
                'learning_container_year': {'common_title': self.lcy.common_title},
                'entities': {'REQUIREMENT_ENTITY': self.requirement_entity.id}
            },
        )
        self.previous_proposal = ProposalLearningUnitFactory(learning_unit_year=self.previous_luy_2)

        self.url_edit = reverse('edit_learning_unit', args=[self.learning_unit_year.id])
        self.url_edit_non_editable = reverse('edit_learning_unit', args=[self.previous_learning_unit_year.id])
        self.context = {
            "learning_unit_year": self.learning_unit_year,
            "request": self.request,
            "user": self.person.user,
            "proposal": self.proposal
        }

    def test_is_not_valid_not_proposal(self):
        self.context['proposal'] = None
        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, MSG_IS_NOT_A_PROPOSAL)
        self.assertEqual(disabled, DISABLED)

    def test_is_not_valid_not_same_lu(self):
        self.context['learning_unit_year'] = self.previous_learning_unit_year
        self.context['proposal'] = self.proposal

        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, MSG_PROPOSAL_NOT_ON_CURRENT_LU)
        self.assertEqual(disabled, DISABLED)

    def test_is_valid(self):
        self.context['learning_unit_year'] = self.learning_unit_year
        self.context['proposal'] = self.proposal

        permission_denied_message, disabled = is_valid_proposal(self.context)
        self.assertEqual(permission_denied_message, "")
        self.assertEqual(disabled, "")

    @override_settings(YEAR_LIMIT_LUE_MODIFICATION=2018)
    def test_li_edit_proposal_as_faculty_manager(self):
        faculty_manager = FacultyManagerFactory()
        self.context['user'] = faculty_manager.person.user

        self.context['proposal'] = self.proposal
        self.context['learning_unit_year'] = self.proposal.learning_unit_year

        result = li_edit_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_proposal_edit',
                _("You can only modify a learning unit when your are linked to its requirement entity"),
                DISABLED
            )
        )

        faculty_manager = FacultyManagerFactory(entity=self.lcy.requirement_entity)
        self.context['user'] = faculty_manager.person.user
        self.context['person'] = faculty_manager.person
        self.proposal.state = ProposalState.CENTRAL.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_edit_proposal(self.context, self.url_edit, "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_proposal_edit', _("Person not in accordance with proposal state"), DISABLED
            )
        )

    def test_li_cancel_proposal_not_accordance_with_proposal_state(self):
        person_faculty_manager = FacultyManagerFactory(entity=self.lcy.requirement_entity).person
        self.context['user'] = person_faculty_manager.user
        self.proposal.state = ProposalState.CENTRAL.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_cancel_proposal(self.context, self.url_edit, "", "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_cancel_proposal', _("Person not in accordance with proposal state"), DISABLED
            )
        )

    def test_li_consolidate_proposal_no_rights_to_consolidate(self):
        person = PersonFactory()
        self.context['user'] = person.user
        result = li_consolidate_proposal(self.context, self.url_edit, "", "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_consolidate_proposal', None, DISABLED
            )
        )

    def test_li_consolidate_proposal_not_good_proposal_state(self):
        self.context['user'] = FacultyManagerFactory(entity=self.lcy.requirement_entity).person.user
        self.proposal.state = ProposalState.SUSPENDED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "", "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_consolidate_proposal', _('Proposal not in eligible state for consolidation'), DISABLED
            )
        )

    def test_li_consolidate_proposal_not_attached_to_entity(self):
        self.context['user'] = FacultyManagerFactory().person.user
        self.proposal.state = ProposalState.ACCEPTED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "", "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_consolidate_proposal',
                _("You can only modify a learning unit when your are linked to its requirement entity"),
                DISABLED
            )
        )

    def test_li_consolidate_proposal(self):
        self.context['user'] = self.manager.person.user
        self.proposal.state = ProposalState.ACCEPTED.name
        self.proposal.save()
        self.context['proposal'] = self.proposal
        result = li_consolidate_proposal(self.context, self.url_edit, "", "")
        self.assertEqual(
            result, self._get_result_data_expected_for_proposal(
                'link_consolidate_proposal', "", "", True
            )
        )

    def test_li_delete_all_lu_cannot_delete_learning_unit_year_according_type(self):
        a_person = FacultyManagerFactory(entity=self.lcy.requirement_entity).person
        self.context['user'] = a_person.user

        lcy_master = LearningContainerYearFactory(
            academic_year=self.current_academic_year,
            container_type=learning_container_year_types.COURSE,
            requirement_entity=self.lcy.requirement_entity
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy_master
        )
        self.context['learning_unit_year'] = learning_unit_yr

        result = li_delete_all_lu(self.context, self.url_edit, '', "#modalDeleteLuy")
        expected = self._get_result_data_expected_delete(
            "link_delete_lus", _("Learning unit type is not deletable")
        )

        self.assertEqual(result, expected)

    def test_li_delete_all_lu_cannot_delete_existing_before_limit(self):
        a_person = FacultyManagerFactory(entity=self.lcy.requirement_entity).person
        self.context['user'] = a_person.user

        lcy_master = LearningContainerYearFactory(
            academic_year=self.previous_academic_year,
            container_type=learning_container_year_types.MASTER_THESIS,
            requirement_entity=self.lcy.requirement_entity
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy_master
        )
        self.context['learning_unit_year'] = learning_unit_yr

        result = li_delete_all_lu(self.context, self.url_edit_non_editable, '', "#modalDeleteLuy")

        expected = {
            'class_li': 'disabled',
            'load_modal': False,
            'url': '#',
            'id_li': 'link_delete_lus',
            'title': _("You can't modify learning unit under year : %(year)d. "
                       "Modifications should be made in EPC under year %(year)d" % {"year": 1}),
            'text': '',
            'data_target': ''
        }

        self.assertEqual(expected, result)

    def test_can_modify_end_year_by_proposal_undefined_group(self):
        person = PersonFactory()
        lcy = LearningContainerYearFactory(academic_year=self.previous_academic_year,
                                           container_type=learning_container_year_types.COURSE)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr)
        self.assertFalse(person.user.has_perm('base.can_edit_learning_unit_proposal_date', learning_unit_yr))

    def test_can_modify_end_year_by_proposal_previous_n_year(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.previous_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        learning_unit_yr.initial_data = {"learning_container_year": lcy}
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.FACULTY.name)
        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(faculty_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal', learning_unit_yr
        ))
        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(central_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal_date', learning_unit_yr
        ))

    def test_faculty_mgr_can_not_modify_end_year_by_proposal_n_year(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.current_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.CENTRAL.name)
        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertFalse(faculty_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal_date',
            learning_unit_yr
        ))

    def test_central_mgr_can_modify_end_year_by_proposal_n_year(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.current_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr)
        self.assertTrue(central_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal_date', learning_unit_yr
        ))

    def test_can_modify_end_year_by_proposal_n_year_plus_one(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.next_academic_yr,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.FACULTY.name)

        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(faculty_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal_date', learning_unit_yr
        ))

        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(central_manager.person.user.has_perm(
            'base.can_edit_learning_unit_proposal_date', learning_unit_yr
        ))

    @patch('learning_unit.auth.predicates.has_faculty_proposal_state', return_value=True)
    def test_can_modify_by_proposal_previous_n_year(self, mock_proposal_state):
        lcy = LearningContainerYearFactory(
            academic_year=self.previous_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.previous_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )

        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.FACULTY.name)

        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(faculty_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(central_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

    def test_can_modify_by_proposal_n_year(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.current_academic_year,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        learning_unit_yr.initial_data = {"learning_container_year": lcy}
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.FACULTY.name)

        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(faculty_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(central_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

    def test_can_modify_by_proposal_n_year_plus_one(self):
        lcy = LearningContainerYearFactory(
            academic_year=self.next_academic_yr,
            container_type=learning_container_year_types.COURSE
        )
        learning_unit_yr = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=LearningUnitFactory(),
            learning_container_year=lcy
        )
        ProposalLearningUnitFactory(learning_unit_year=learning_unit_yr, state=ProposalState.FACULTY.name)

        faculty_manager = FacultyManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(faculty_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

        central_manager = CentralManagerFactory(entity=lcy.requirement_entity)
        self.assertTrue(central_manager.person.user.has_perm('base.can_edit_learning_unit_proposal', learning_unit_yr))

    def _build_user_with_permission_to_consolidate(self):
        a_person = PersonFactory()
        a_person.user.user_permissions.add(Permission.objects.get(codename="can_consolidate_learningunit_proposal"))
        return a_person.user

    def _get_result_data_expected_for_proposal(self, id_li, title, class_li, load_modal=False):
        if class_li != "":
            url = "#"
        else:
            url = self.url_edit
        return {
            'load_modal': load_modal,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': class_li,
            'text': "",
            'js_script': "",
            'data_target': '',

        }

    def _get_result_data_expected(self, id_li, title='', url="#", load_modal=False):

        return {
            'load_modal': False,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': self._get_class(title),
            'text': '',
            'data_target': '',
        }

    def _get_result_data_expected_delete(self, id_li, title='', load_modal=False, data_target='', url="#"):

        return {
            'load_modal': load_modal,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': self._get_class(title),
            'text': '',
            'data_target': data_target,
        }

    def _get_class(self, title):
        return DISABLED if title != '' else ''

    def _get_result_data_expected_for_proposal_suppression(self, id_li, title, class_li):
        if class_li != "":
            url = "#"
        else:
            url = self.url_edit
        return {
            'load_modal': False,
            'id_li': id_li,
            'url': url,
            'title': title,
            'class_li': class_li,
            'text': "",
            'data_target': "",

        }
