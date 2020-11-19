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
import collections

import factory.fuzzy
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm, LearningContainerYearModelForm, LearningContainerModelForm
from base.forms.learning_unit.learning_unit_create_2 import FullForm, FACULTY_OPEN_FIELDS, \
    FULL_READ_ONLY_FIELDS, PROPOSAL_READ_ONLY_FIELDS
from base.models.entity_version import EntityVersion
from base.models.enums import learning_unit_year_subtypes, learning_container_year_types, organization_type, \
    learning_unit_year_periodicity
from base.models.enums.component_type import DEFAULT_ACRONYM_COMPONENT
from base.models.enums.internship_subtypes import TEACHING_INTERNSHIP
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES
from base.models.enums.learning_container_year_types import INTERNSHIP, LearningContainerYearType
from base.models.enums.learning_unit_year_periodicity import ANNUAL
from base.models.enums.organization_type import ACADEMIC_PARTNER
from base.models.enums.person_source_type import DISSERTATION
from base.models.learning_component_year import LearningComponentYear
from base.models.learning_container import LearningContainer
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear, MAXIMUM_CREDITS
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.business.learning_units import GenerateContainer, GenerateAcademicYear
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import FacultyManagerGroupFactory, CentralManagerGroupFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from reference.tests.factories.language import LanguageFactory, FrenchLanguageFactory


def _instanciate_form(academic_year, person=None, post_data=None, learning_unit_instance=None, start_year=None,
                      proposal_type=None):
    if not person:
        person = PersonFactory()
    return FullForm(person, academic_year, learning_unit_instance=learning_unit_instance, data=post_data,
                    start_year=start_year, proposal_type=proposal_type)


def get_valid_form_data(academic_year, person, learning_unit_year=None):
    entities = create_entities_hierarchy()
    PersonEntityFactory(person=person, entity=entities['root_entity'], with_child=True)
    requirement_entity_version = entities['child_one_entity_version']
    organization = OrganizationFactory(type=organization_type.MAIN)
    campus = CampusFactory(organization=organization)
    language = FrenchLanguageFactory()

    if not learning_unit_year:
        learning_container = LearningContainerFactory()
        container_year = LearningContainerYearFactory(
            academic_year=academic_year,
            learning_container=learning_container
        )

        learning_unit_full = LearningUnitFactory(
            learning_container=learning_container,
            start_year=academic_year,
            end_year=academic_year,
        )

        learning_unit_year = LearningUnitYearFactory.build(
            academic_year=academic_year,
            learning_unit=learning_unit_full,
            learning_container_year=container_year,
            subtype=learning_unit_year_subtypes.FULL,
            campus=campus,
            language=language,
            periodicity=learning_unit_year_periodicity.ANNUAL
        )

    cm_lcy = LearningComponentYear.objects.filter(learning_unit_year=learning_unit_year).first()
    pp_lcy = LearningComponentYear.objects.filter(learning_unit_year=learning_unit_year).last()

    return {
        # Learning unit year data model form
        'acronym': learning_unit_year.acronym,
        'acronym_0': learning_unit_year.acronym[0],
        'acronym_1': learning_unit_year.acronym[1:],
        'subtype': learning_unit_year.subtype,
        'academic_year': learning_unit_year.academic_year.id,
        'specific_title': learning_unit_year.specific_title,
        'specific_title_english': learning_unit_year.specific_title_english,
        'credits': learning_unit_year.credits,
        'session': learning_unit_year.session,
        'quadrimester': learning_unit_year.quadrimester,
        'status': learning_unit_year.status,
        'internship_subtype': None,
        'attribution_procedure': learning_unit_year.attribution_procedure,
        'campus': learning_unit_year.campus.id,
        'language': learning_unit_year.language.pk,
        'periodicity': learning_unit_year.periodicity,

        # Learning unit data model form
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,
        'other_remark': learning_unit_year.learning_unit.other_remark,

        # Learning container year data model form
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'container_type': learning_unit_year.learning_container_year.container_type,
        'type_declaration_vacant': learning_unit_year.learning_container_year.type_declaration_vacant,
        'team': learning_unit_year.learning_container_year.team,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant,

        'requirement_entity': requirement_entity_version.id,
        'allocation_entity': requirement_entity_version.id,
        'additional_entity_1': '',

        # Learning component year data model form
        'component-0-id': cm_lcy and cm_lcy.pk,
        'component-1-id': pp_lcy and pp_lcy.pk,
        'component-TOTAL_FORMS': '2',
        'component-INITIAL_FORMS': '0' if not cm_lcy else '2',
        'component-MAX_NUM_FORMS': '2',
        'component-0-hourly_volume_total_annual': 20,
        'component-0-hourly_volume_partial_q1': 10,
        'component-0-hourly_volume_partial_q2': 10,
        'component-0-planned_classes': 1,
        'component-1-hourly_volume_total_annual': 20,
        'component-1-hourly_volume_partial_q1': 10,
        'component-1-hourly_volume_partial_q2': 10,
        'component-1-planned_classes': 1,
    }


class LearningUnitFullFormContextMixin(TestCase):
    """This mixin is used in this test file in order to setup an environment for testing FULL FORM"""
    @classmethod
    def setUpTestData(cls):
        cls.initial_language = FrenchLanguageFactory()
        cls.initial_campus = CampusFactory(name='Louvain-la-Neuve', organization__type=organization_type.MAIN)
        cls.current_academic_year = create_current_academic_year()
        # Creation of a LearningContainerYear and all related models
        cls.learn_unit_structure = GenerateContainer(cls.current_academic_year, cls.current_academic_year)

        start_year = AcademicYearFactory(year=cls.current_academic_year.year - 3)
        end_year = AcademicYearFactory(year=cls.current_academic_year.year + 7)
        cls.acs = GenerateAcademicYear(start_year=start_year, end_year=end_year).academic_years

    def setUp(self):
        self.learning_unit_year = LearningUnitYear.objects.get(
            learning_unit=self.learn_unit_structure.learning_unit_full,
            academic_year=self.current_academic_year
        )
        del self.acs[3]
        for ac in self.acs:
            LearningUnitYearFactory(academic_year=ac, learning_unit=self.learning_unit_year.learning_unit)
        self.acs.insert(3, self.current_academic_year)
        self.person = PersonFactory()
        self.post_data = get_valid_form_data(self.current_academic_year, person=self.person)


class TestFullFormInit(LearningUnitFullFormContextMixin):
    """Unit tests for FullForm.__init__()"""

    def test_case_start_year_and_learning_unit_instance_kwarg_are_missing(self):
        with self.assertRaises(AttributeError):
            FullForm(self.person, self.learning_unit_year.academic_year, post_data=self.post_data)

    def test_disable_fields_full_with_faculty_manager(self):
        self.person.user.groups.add(FacultyManagerGroupFactory())
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled}
        self.assertTrue(FACULTY_OPEN_FIELDS not in disabled_fields)

    def test_disable_fields_full_proposal(self):
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit, proposal=True)
        self.assertTrue(form.fields['academic_year'].disabled)
        self.assertTrue(form.fields['container_type'].disabled)

    def test_disable_fields_full_proposal_with_faculty_manager(self):
        self.person.user.groups.add(FacultyManagerGroupFactory())
        form = FullForm(
            self.person,
            self.learning_unit_year.academic_year,
            learning_unit_instance=self.learning_unit_year.learning_unit,
            proposal=True
        )

        for elem in PROPOSAL_READ_ONLY_FIELDS:
            self.assertEqual(form.fields[elem].disabled, True)
            self.assertEqual(form.fields['academic_year'].disabled, True)

    def test_subtype_is_full(self):
        learn_unit_year = LearningUnitYearFactory(
            subtype=learning_unit_year_subtypes.FULL,
            learning_container_year__requirement_entity=None,
            learning_container_year__allocation_entity=None
        )
        form = _instanciate_form(learn_unit_year.academic_year, learning_unit_instance=learn_unit_year.learning_unit)
        self.assertEqual(form.subtype, learning_unit_year_subtypes.FULL)

    def test_wrong_instance_arg(self):
        wrong_instance = PersonFactory()
        with self.assertRaises(ValueError):
            _instanciate_form(AcademicYearFactory(year=1980), learning_unit_instance=wrong_instance)

    def test_model_forms_case_creation(self):
        form_classes_expected = [LearningUnitModelForm, LearningUnitYearModelForm, LearningContainerModelForm,
                                 LearningContainerYearModelForm]
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        for cls in form_classes_expected:
            self.assertIsInstance(form.forms[cls], cls)

    def test_initial_values_of_forms_case_creation(self):
        full_form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                      start_year=self.current_academic_year.year)
        expected_initials = {
            LearningUnitYearModelForm: {
                'status': True, 'academic_year': self.current_academic_year,
                'language': self.initial_language
            },
            LearningContainerYearModelForm: {
                'campus': self.initial_campus
            }
        }
        for form_class, initial in expected_initials.items():
            self.assertEqual(full_form.forms[form_class].initial, initial)

    def test_model_forms_case_update(self):
        learn_unit_year = self.learning_unit_year
        form = _instanciate_form(self.learning_unit_year.academic_year,
                                 post_data=self.post_data, person=self.person,
                                 learning_unit_instance=learn_unit_year.learning_unit)

        self.assertEqual(form.forms[LearningUnitModelForm].instance, learn_unit_year.learning_unit)
        self.assertEqual(form.forms[LearningContainerModelForm].instance,
                         learn_unit_year.learning_container_year.learning_container)
        self.assertEqual(form.forms[LearningUnitYearModelForm].instance, learn_unit_year)
        self.assertEqual(form.forms[LearningContainerYearModelForm].instance, learn_unit_year.learning_container_year)

    def test_academic_years_restriction_for_central_manager(self):
        self.person.user.groups.add(CentralManagerGroupFactory())
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        start_year=self.learning_unit_year.academic_year.year,
                        postposal=True)
        actual_choices = [choice[0] for choice in form.fields["academic_year"].choices if choice[0] != '']
        expected_choices = [acy.id for acy in self.acs[3:10]]

        self.assertCountEqual(actual_choices, expected_choices)

    def test_academic_years_restriction_for_faculty_manager(self):
        self.person.user.groups.add(FacultyManagerGroupFactory())
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        start_year=self.learning_unit_year.academic_year.year,
                        postposal=True)
        actual_choices = [choice[0] for choice in form.fields["academic_year"].choices if choice[0] != '']
        expected_choices = [acy.id for acy in self.acs[3:6]]
        self.assertCountEqual(actual_choices, expected_choices)

    def test_disable_fields_full_with_faculty_manager_and_central_manager(self):
        self.person.user.groups.add(FacultyManagerGroupFactory())
        self.person.user.groups.add(CentralManagerGroupFactory())
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled}
        self.assertEqual(disabled_fields, FULL_READ_ONLY_FIELDS.union({'internship_subtype'}))

    def test_disable_fields_acronym_with_central_manager_and_other_collective(self):
        self.person.user.groups.add(CentralManagerGroupFactory())
        self.learning_unit_year.learning_container_year.container_type = LearningContainerYearType.OTHER_COLLECTIVE.name
        self.learning_unit_year.learning_container_year.save()
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled}
        self.assertTrue("acronym" not in disabled_fields)

    def test_disable_fields_acronym_with_faculty_manager_and_other_collective(self):
        self.person.user.groups.add(FacultyManagerGroupFactory())
        self.learning_unit_year.learning_container_year.container_type = LearningContainerYearType.OTHER_COLLECTIVE.name
        self.learning_unit_year.learning_container_year.save()
        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit)
        disabled_fields = {key for key, value in form.fields.items() if value.disabled}
        self.assertTrue("acronym" not in disabled_fields)


class TestFullFormIsValid(LearningUnitFullFormContextMixin):
    """Unit tests for is_valid() """

    def _assert_equal_values(self, obj, dictionary, fields_to_validate):
        for field in fields_to_validate:
            self.assertEqual(getattr(obj, field), dictionary[field], msg='Error field = {}'.format(field))

    def test_creation_case_correct_post_data(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year, person=self.person)
        self.assertTrue(form.is_valid(), form.errors)
        self._test_learning_unit_model_form_instance(form)
        self._test_learning_unit_year_model_form_instance(form)
        self._test_learning_container_model_form_instance(form)
        self._test_learning_container_year_model_form_instance(form)

    def _test_learning_unit_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningUnitModelForm]
        fields_to_validate = ['faculty_remark', 'other_remark']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def _test_learning_container_model_form_instance(self, full_form):
        self.assertIn(LearningContainerModelForm, full_form.forms)

    def _test_learning_unit_year_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningUnitYearModelForm]
        fields_to_validate = ['acronym', 'specific_title', 'specific_title_english', 'credits',
                              'session', 'quadrimester', 'status', 'internship_subtype', 'attribution_procedure',
                              'subtype', 'periodicity']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)
        self.assertEqual(form_instance.instance.academic_year.id, self.post_data['academic_year'])

    def _test_learning_container_year_model_form_instance(self, full_form):
        form_instance = full_form.forms[LearningContainerYearModelForm]
        fields_to_validate = ['container_type', 'common_title', 'common_title_english',
                              'type_declaration_vacant', 'team', 'is_vacant']
        self._assert_equal_values(form_instance.instance, self.post_data, fields_to_validate)

    def test_creation_case_wrong_learning_unit_data(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_creation_case_wrong_learning_unit_year_data(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_creation_case_wrong_learning_container_year_data(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_creation_case_not_same_entities_container(self):
        entity_version = EntityVersionFactory(end_date=None)
        # Set another requirement entity
        self.learning_unit_year.learning_container_year.requirement_entity = entity_version.entity
        self.learning_unit_year.learning_container_year.save()

        form = _instanciate_form(
            self.current_academic_year,
            post_data=self.post_data,
            learning_unit_instance=self.learning_unit_year.learning_unit,
            start_year=self.current_academic_year.year
        )
        self.assertFalse(form.is_valid())

    def test_update_case_correct_data(self):
        self.post_data['periodicity'] = ANNUAL
        form = _instanciate_form(
            self.current_academic_year,
            post_data=self.post_data,
            person=self.person,
            learning_unit_instance=self.learning_unit_year.learning_unit
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_filter_additional_requirement_entity(self):
        partner = EntityVersionFactory(
            parent=None,
            entity__organization__type=ACADEMIC_PARTNER
        )
        self.post_data["additional_requirement_entity_1"] = partner.id
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit, person=self.person)
        self.assertTrue(form.is_valid(), form.errors)

    def test_update_case_wrong_learning_unit_data(self):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    def test_update_case_wrong_learning_unit_year_data(self):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    def test_update_case_wrong_learning_container_year_data(self):
        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid())

    def test_update_case_wrong_entity_version_start_year_data(self):
        allocation_entity_id = self.post_data['allocation_entity']
        allocation_entity = EntityVersion.objects.get(pk=allocation_entity_id)
        start_date = self.learning_unit_year.academic_year.start_date
        allocation_entity.start_date = start_date.replace(year=start_date.year + 2)
        allocation_entity.save()

        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=self.post_data, person=self.person,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid(), form.errors)

    def test_update_case_credits_too_high_3_digits(self):
        post_data = dict(self.post_data)
        post_data['credits'] = MAXIMUM_CREDITS + 1

        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=post_data, person=self.person,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(
            form.errors[0]['credits'],
            [_('Ensure this value is less than or equal to %(limit_value)s.') % {
                'limit_value': MAXIMUM_CREDITS
            }]
        )

    def test_update_case_credits_too_high_4_digits(self):
        post_data = dict(self.post_data)
        post_data['credits'] = factory.fuzzy.FuzzyDecimal(1000, 100000, 2).fuzz()

        form = _instanciate_form(self.learning_unit_year.academic_year, post_data=post_data, person=self.person,
                                 learning_unit_instance=self.learning_unit_year.learning_unit)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(
            form.errors[0]['credits'],
            [_('Ensure this value is less than or equal to %(limit_value)s.') % {
                'limit_value': MAXIMUM_CREDITS
            }]
        )


class TestFullFormSave(LearningUnitFullFormContextMixin):
    """Unit tests for save() """

    def _get_initial_counts(self):
        return collections.OrderedDict({
            LearningContainer: self._count_records(LearningContainer),
            LearningContainerYear: self._count_records(LearningContainerYear),
            LearningUnit: self._count_records(LearningUnit),
            LearningUnitYear: self._count_records(LearningUnitYear),
            LearningComponentYear: self._count_records(LearningComponentYear),
        })

    def test_when_update_instance(self):
        self.post_data = get_valid_form_data(self.current_academic_year, self.person, self.learning_unit_year)

        self.learning_unit_year.learning_container_year.additional_entity_1 = None
        self.learning_unit_year.learning_container_year.additional_entity_2 = None
        self.learning_unit_year.learning_container_year.save()

        initial_counts = self._get_initial_counts()
        self.post_data['credits'] = 99

        form = FullForm(self.person, self.learning_unit_year.academic_year,
                        learning_unit_instance=self.learning_unit_year.learning_unit, data=self.post_data)

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(LearningUnitYear.objects.get(pk=self.learning_unit_year.id).credits, 99)

        for model_class, initial_count in initial_counts.items():
            current_count = self._count_records(model_class)
            self.assertEqual(current_count, initial_count, model_class.objects.all())

    def test_when_delete_additionnal_entity(self):
        post_data = get_valid_form_data(self.current_academic_year, self.person, self.learning_unit_year)
        # Assert additionnal entity exists exists
        if not self.learning_unit_year.learning_container_year.additional_entity_1:
            self.learning_unit_year.learning_container_year.additional_entity_1 = EntityFactory()
            self.learning_unit_year.learning_container_year.save()
        # Assert repartition volumes are set for additional entity
        component_queryset = LearningComponentYear.objects.filter(
            learning_unit_year__learning_container_year=self.learning_unit_year.learning_container_year
        )
        component_queryset.update(repartition_volume_additional_entity_1=15.0)

        # Removing additionnal entity
        post_data["additional_entity_1"] = ""

        self.assertEqual(component_queryset.count(), 4)  # Assert we are testing for Full AND Partim (2 components each)

        form = FullForm(
            self.person,
            self.learning_unit_year.academic_year,
            learning_unit_instance=self.learning_unit_year.learning_unit,
            data=post_data
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.learning_unit_year.learning_container_year.refresh_from_db()
        self.assertIsNone(self.learning_unit_year.learning_container_year.additional_entity_1)
        self.learning_unit_year.learning_container_year.refresh_from_db()
        self.assertIsNotNone(self.learning_unit_year.learning_container_year.requirement_entity)
        self.assertIsNotNone(self.learning_unit_year.learning_container_year.allocation_entity)
        for component in component_queryset:
            self.assertIsNone(component.repartition_volume_additional_entity_1)

    def test_default_acronym_component(self):
        default_acronym_component = {
            LECTURING: "PM",
            PRACTICAL_EXERCISES: "PP",
            None: "NT"
        }
        self.assertEqual(default_acronym_component, DEFAULT_ACRONYM_COMPONENT)

    def test_when_create_instance(self):
        initial_counts = self._get_initial_counts()
        acronym = 'LAGRO1200'
        new_learning_unit_year = LearningUnitYearFactory.build(
            acronym=acronym,
            academic_year=self.current_academic_year,
            subtype=learning_unit_year_subtypes.FULL,
            language=self.initial_language,
            learning_container_year__academic_year=self.current_academic_year,
            learning_container_year__container_type=learning_container_year_types.COURSE,
            campus=self.initial_campus
        )
        post_data = get_valid_form_data(self.current_academic_year, person=self.person,
                                        learning_unit_year=new_learning_unit_year)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year)
        self.assertTrue(form.is_valid(), form.errors)
        saved_luy = form.save()
        self.assertEqual(LearningUnitYear.objects.filter(acronym='LAGRO1200').count(), 1)
        self.assertEqual(LearningComponentYear.objects.filter(
            learning_unit_year__learning_container_year=self.learning_unit_year.learning_container_year).count(), 4)

        self._assert_correctly_create_records_in_all_learning_unit_structure(initial_counts)
        self.assertEqual(LearningComponentYear.objects.filter(
            learning_unit_year=saved_luy
        ).count(), 2)
        self.assertEqual(
            LearningComponentYear.objects.get(
                learning_unit_year=saved_luy, type=LECTURING).acronym, "PM")
        self.assertEqual(
            LearningComponentYear.objects.get(
                learning_unit_year=saved_luy, type=PRACTICAL_EXERCISES).acronym, "PP")

    def test_when_type_is_internship(self):
        self.learning_unit_year.learning_container_year.additional_entity_1 = None
        self.learning_unit_year.learning_container_year.additional_entity_2 = None
        self.learning_unit_year.learning_container_year.save()

        self.post_data['credits'] = 99
        self.post_data['container_type'] = INTERNSHIP
        self.post_data['internship_subtype'] = TEACHING_INTERNSHIP

        form = FullForm(self.person,
                        self.learning_unit_year.academic_year,
                        start_year=self.current_academic_year,
                        data=self.post_data)

        self.assertTrue(form.is_valid(), form.errors)
        saved_luy = form.save()

        self.assertEqual(saved_luy.credits, 99)
        self.assertEqual(saved_luy.learning_container_year.container_type, INTERNSHIP)
        self.assertEqual(saved_luy.internship_subtype, TEACHING_INTERNSHIP)
        learning_component_year_list = LearningComponentYear.objects.filter(
            learning_unit_year__learning_container_year=saved_luy.learning_container_year
        )
        self.assertEqual(learning_component_year_list.count(), 2)
        self.assertEqual(
            LearningComponentYear.objects.get(
                learning_unit_year=saved_luy, type=LECTURING).acronym, "PM")
        self.assertEqual(
            LearningComponentYear.objects.get(
                learning_unit_year=saved_luy, type=PRACTICAL_EXERCISES).acronym, "PP")

    def test_when_type_is_dissertation(self):
        self.learning_unit_year.learning_container_year.additional_entity_1 = None
        self.learning_unit_year.learning_container_year.additional_entity_2 = None
        self.learning_unit_year.learning_container_year.save()

        self.post_data['credits'] = 99
        self.post_data['container_type'] = DISSERTATION

        form = FullForm(self.person,
                        self.learning_unit_year.academic_year,
                        start_year=self.current_academic_year,
                        data=self.post_data)

        self.assertTrue(form.is_valid(), form.errors)
        saved_luy = form.save()

        self.assertEqual(saved_luy.credits, 99)
        self.assertEqual(saved_luy.learning_container_year.container_type, DISSERTATION)
        learning_component_year_list = LearningComponentYear.objects.filter(
            learning_unit_year__learning_container_year=saved_luy.learning_container_year
        )
        self.assertEqual(learning_component_year_list.count(), 1)
        learning_component_year = LearningComponentYear.objects.get(learning_unit_year=saved_luy, type=None)
        self.assertEqual(learning_component_year.acronym, DEFAULT_ACRONYM_COMPONENT[None])
        self.assertEqual(learning_component_year.type, None)

    def _assert_correctly_create_records_in_all_learning_unit_structure(self, initial_counts):
        number_of_components = 2  # container_type == COURSE ==> 1 TP / 1 CM
        self.assertEqual(self._count_records(LearningContainer), initial_counts[LearningContainer] + 1)
        self.assertEqual(self._count_records(LearningContainerYear), initial_counts[LearningContainerYear] + 1)
        self.assertEqual(self._count_records(LearningUnit), initial_counts[LearningUnit] + 1)
        self.assertEqual(self._count_records(LearningUnitYear), initial_counts[LearningUnitYear] + 1)
        self.assertEqual(self._count_records(LearningComponentYear),
                         initial_counts[LearningComponentYear] + number_of_components)

    @staticmethod
    def _count_records(model_class):
        return model_class.objects.all().count()


class TestFullFormValidateSameEntitiesContainer(LearningUnitFullFormContextMixin):
    """Unit tests for FullForm._validate_same_entities_container()"""

    def test_when_same_entities_container(self):
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertTrue(form.is_valid(), form.errors)

    def test_when_not_same_entities_container_case_container_type_master_thesis(self):
        post_data = self._get_post_data_with_different_entities_container_year(
            learning_container_year_types.MASTER_THESIS)
        form = _instanciate_form(self.current_academic_year, post_data=post_data,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_when_not_same_entities_container_case_container_type_internship(self):
        post_data = self._get_post_data_with_different_entities_container_year(learning_container_year_types.INTERNSHIP)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def test_when_not_same_entities_container_case_container_type_dissertation(self):
        post_data = self._get_post_data_with_different_entities_container_year(
            learning_container_year_types.DISSERTATION)
        form = _instanciate_form(self.current_academic_year, post_data=post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())

    def _get_post_data_with_different_entities_container_year(self, container_type):
        container_year = LearningContainerYearFactory.build(academic_year=self.current_academic_year,
                                                            container_type=container_type)
        learning_unit_year = LearningUnitYearFactory.build(academic_year=self.current_academic_year,
                                                           learning_container_year=container_year,
                                                           subtype=learning_unit_year_subtypes.FULL)
        post_data = get_valid_form_data(self.current_academic_year, person=self.person,
                                        learning_unit_year=learning_unit_year)
        post_data['allocation_entity-entity'] = EntityVersionFactory().id
        return post_data

    def test_when_volumes_entities_incorrect(self):
        self.post_data['additional_entity_1'] = self.post_data['requirement_entity']
        self.post_data['component-0-repartition_volume_requirement_entity'] = 5
        self.post_data['component-0-repartition_volume_additional_entity_1'] = 10
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertFalse(form.is_valid())
        self.post_data['component-0-repartition_volume_requirement_entity'] = 10
        self.post_data['component-0-repartition_volume_additional_entity_1'] = 10
        form = _instanciate_form(self.current_academic_year, post_data=self.post_data, person=self.person,
                                 start_year=self.current_academic_year.year)
        self.assertTrue(form.is_valid(), form.errors)
