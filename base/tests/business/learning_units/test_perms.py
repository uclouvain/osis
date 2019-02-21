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
import datetime
from unittest import mock
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from base.tests.factories.user import UserFactory
from base.business.learning_units.xls_comparison import prepare_xls_content, \
    _get_learning_unit_yrs_on_2_different_years, translate_status, create_xls_comparison, \
    XLS_FILENAME, XLS_DESCRIPTION, LEARNING_UNIT_TITLES, WORKSHEET_TITLE, CELLS_MODIFIED_NO_BORDER, DATA, \
    _check_changes_other_than_code_and_year, CELLS_TOP_BORDER, _check_changes, _get_proposal_data, \
    get_representing_string
from osis_common.document import xls_build
from base.tests.factories.business.learning_units import GenerateContainer
from base.models.enums import entity_container_year_link_type
from base.models.entity_container_year import EntityContainerYear
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_type, organization_type
from base.models.learning_component_year import LearningComponentYear
from base.models.enums.component_type import LECTURING, PRACTICAL_EXERCISES
from base.models.entity_version import get_last_version
from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY, ALLOCATION_ENTITY, \
    ADDITIONAL_REQUIREMENT_ENTITY_1, ADDITIONAL_REQUIREMENT_ENTITY_2
from base.models.enums.component_type import DEFAULT_ACRONYM_COMPONENT
from base.tests.factories.learning_component_year import LecturingLearningComponentYearFactory, \
    PracticalLearningComponentYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.business.learning_units.perms import is_eligible_to_modify_end_year_by_proposal
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth.models import Permission

from base.business.learning_units.perms import MSG_EXISTING_PROPOSAL_IN_EPC, MSG_NO_ELIGIBLE_TO_MODIFY_END_DATE, \
    MSG_CAN_EDIT_PROPOSAL_NO_LINK_TO_ENTITY, \
    MSG_NOT_PROPOSAL_STATE_FACULTY, MSG_NOT_ELIGIBLE_TO_EDIT_PROPOSAL, \
    MSG_PERSON_NOT_IN_ACCORDANCE_WITH_PROPOSAL_STATE, MSG_ONLY_IF_YOUR_ARE_LINK_TO_ENTITY, MSG_NOT_GOOD_RANGE_OF_YEARS, \
    MSG_NO_RIGHTS_TO_CONSOLIDATE, \
    MSG_NOT_ELIGIBLE_TO_CONSOLIDATE_PROPOSAL, MSG_PROPOSAL_NOT_IN_CONSOLIDATION_ELIGIBLE_STATES, \
    MSG_NOT_ELIGIBLE_TO_DELETE_LU, MSG_CAN_DELETE_ACCORDING_TO_TYPE, MSG_PROPOSAL_IS_ON_AN_OTHER_YEAR, \
    can_modify_end_year_by_proposal, is_eligible_to_modify_by_proposal, can_modify_by_proposal, \
    MSG_NOT_ELIGIBLE_TO_MODIFY_END_YEAR_PROPOSAL_ON_THIS_YEAR, MSG_NOT_ELIGIBLE_TO_PUT_IN_PROPOSAL_ON_THIS_YEAR
from base.templatetags.learning_unit_li import li_edit_lu, li_edit_date_lu, li_modification_proposal, is_valid_proposal, \
    MSG_IS_NOT_A_PROPOSAL, MSG_PROPOSAL_NOT_ON_CURRENT_LU, DISABLED, li_suppression_proposal, li_cancel_proposal, \
    li_edit_proposal, li_consolidate_proposal, li_delete_all_lu
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import CentralManagerFactory, FacultyManagerFactory
from base.tests.factories.proposal_learning_unit import ProposalLearningUnitFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.user import UserFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type
from base.models.enums import learning_container_year_types
from base.models.enums.proposal_state import ProposalState
from django.conf import settings
from django.core.exceptions import PermissionDenied


class TestPerms(TestCase):

    def setUp(self):
        self.learning_unit = LearningUnitFactory()
        self.previous_learning_unit = LearningUnitFactory(existing_proposal_in_epc=False)
        self.current_academic_year = create_current_academic_year()
        self.previous_academic_year = AcademicYearFactory(year=self.current_academic_year.year-1)
        self.next_academic_yr = AcademicYearFactory(year=self.current_academic_year.year+1)
        self.lcy = LearningContainerYearFactory(academic_year=self.current_academic_year,
                                                container_type=learning_container_year_types.COURSE)

    def test_not_is_eligible_to_modify_end_year_by_proposal(self):
        lu = LearningUnitFactory(existing_proposal_in_epc=False)
        learning_unit_year_without_proposal = LearningUnitYearFactory(
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=lu,
            learning_container_year=self.lcy
        )
        person_faculty_manager = FacultyManagerFactory()

        with self.assertRaises(PermissionDenied) as perm_ex:
            is_eligible_to_modify_end_year_by_proposal(learning_unit_year_without_proposal,
                                                       person_faculty_manager,
                                                       True)
            self.assertEqual('{}'.format(perm_ex.exception), MSG_NOT_ELIGIBLE_TO_MODIFY_END_YEAR_PROPOSAL_ON_THIS_YEAR)

    def test_is_eligible_to_modify_end_year_by_proposal(self):
        lu = LearningUnitFactory(existing_proposal_in_epc=False)
        learning_unit_year_without_proposal = LearningUnitYearFactory(
            academic_year=self.next_academic_yr,
            subtype=learning_unit_year_subtypes.FULL,
            learning_unit=lu,
            learning_container_year=self.lcy
        )
        proposal = ProposalLearningUnitFactory(learning_unit_year=learning_unit_year_without_proposal)
        person_faculty_manager = FacultyManagerFactory()

        with self.assertRaises(PermissionDenied) as perm_ex:
            is_eligible_to_modify_end_year_by_proposal(learning_unit_year_without_proposal,
                                                       person_faculty_manager,
                                                       True)
            self.assertEqual('{}'.format(perm_ex.exception), MSG_NOT_ELIGIBLE_TO_MODIFY_END_YEAR_PROPOSAL_ON_THIS_YEAR)
