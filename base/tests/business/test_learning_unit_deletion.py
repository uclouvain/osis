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
import datetime

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from assistant.models.tutoring_learning_unit_year import TutoringLearningUnitYear
from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from attribution.tests.factories.attribution import AttributionNewFactory
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.business import learning_unit_deletion
from base.models.enums import entity_container_year_link_type
from base.models.enums import entity_type
from base.models.enums import learning_container_year_types
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_class_year import LearningClassYear
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit_component import LearningUnitComponent
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory


class LearningUnitYearDeletion(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=timezone.now().year)

    def test_check_related_partims_deletion(self):
        l_container_year = LearningContainerYearFactory()
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.FULL)
        msg = learning_unit_deletion._check_related_partims_deletion(l_container_year)
        self.assertEqual(len(msg.values()), 0)

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        group_1 = GroupElementYearFactory(child_leaf=l_unit_2)
        group_2 = GroupElementYearFactory(child_leaf=l_unit_2)

        component = LearningUnitComponentFactory(learning_unit_year=l_unit_2)

        attribution_1 = AttributionNewFactory()
        attribution_2 = AttributionNewFactory()

        AttributionChargeNewFactory(learning_component_year=component.learning_component_year,
                                    attribution=attribution_1)
        AttributionChargeNewFactory(learning_component_year=component.learning_component_year,
                                    attribution=attribution_1)
        AttributionChargeNewFactory(learning_component_year=component.learning_component_year,
                                    attribution=attribution_2)

        msg = learning_unit_deletion._check_related_partims_deletion(l_container_year)
        msg = list(msg.values())

        self.assertEqual(len(msg), 5)
        self.assertIn(_("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s")
                      % {'subtype': _('The partim'),
                         'acronym': l_unit_2.acronym,
                         'year': l_unit_2.academic_year,
                         'count': 3},
                      msg)

        msg_delete_tutor = _("%(subtype)s %(acronym)s is assigned to %(tutor)s for the year %(year)s")
        self.assertIn(msg_delete_tutor % {'subtype': _('The partim'),
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_1.tutor},
                      msg)
        self.assertIn(msg_delete_tutor % {'subtype': _('The partim'),
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_2.tutor},
                      msg)

        msg_delete_offer_type = _(
            '%(subtype)s %(acronym)s is included in the group %(group)s of the program %(program)s for the year %(year)s')

        self.assertIn(msg_delete_offer_type
                      % {'subtype': _('The partim'),
                         'acronym': l_unit_2.acronym,
                         'group': group_1.parent.acronym,
                         'program': group_1.parent.education_group_type,
                         'year': l_unit_2.academic_year},
                      msg)
        self.assertIn(msg_delete_offer_type
                      % {'subtype': _('The partim'),
                         'acronym': l_unit_2.acronym,
                         'group': group_2.parent.acronym,
                         'program': group_2.parent.education_group_type,
                         'year': l_unit_2.academic_year},
                      msg)

    def test_check_learning_unit_year_deletion(self):
        l_container_year = LearningContainerYearFactory(acronym="LBIR1212", academic_year=self.academic_year)
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.FULL)
        msg = learning_unit_deletion.check_learning_unit_year_deletion(l_unit_1)

        msg = list(msg.values())
        self.assertEqual(msg, [])

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212A", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)
        l_unit_3 = LearningUnitYearFactory(acronym="LBIR1212B", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_1)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        msg = learning_unit_deletion.check_learning_unit_year_deletion(l_unit_1)

        msg = list(msg.values())
        self.assertEqual(len(msg), 2)

    def test_delete_next_years(self):
        l_unit = LearningUnitFactory()

        dict_learning_units = {}
        for year in range(2000, 2017):
            academic_year = AcademicYearFactory(year=year)
            dict_learning_units[year] = LearningUnitYearFactory(academic_year=academic_year, learning_unit=l_unit)

        msg = learning_unit_deletion.delete_from_given_learning_unit_year(dict_learning_units[2007])
        self.assertEqual(LearningUnitYear.objects.filter(academic_year__year__gte=2007, learning_unit=l_unit).count(),
                         0)
        self.assertEqual(len(msg), 2017-2007)

    def test_delete_partim_from_full(self):
        l_container_year = LearningContainerYearFactory()
        l_unit_year = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.FULL,
                                              learning_container_year=l_container_year)

        l_unit_partim_1 = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.PARTIM,
                                                  learning_container_year=l_container_year)
        l_unit_partim_2 = LearningUnitYearFactory(subtype=learning_unit_year_subtypes.PARTIM,
                                                  learning_container_year=l_container_year)

        learning_unit_deletion.delete_from_given_learning_unit_year(l_unit_year)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=l_unit_partim_1.id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=l_unit_partim_2.id)

    def test_delete_learning_unit_component_class(self):
        # Composant annualisé est associé à son composant et à son conteneur annualisé
        learning_component_year = LearningComponentYearFactory(title="Cours magistral",
                                                               acronym="/C",
                                                               comment="TEST")
        learning_container_year = learning_component_year.learning_container_year

        number_classes = 10
        for x in range(number_classes):
            LearningClassYearFactory(learning_component_year=learning_component_year)

        # Association du conteneur et de son composant dont les années académiques diffèrent l'une de l'autre
        learning_unit_component = LearningUnitComponentFactory(learning_component_year=learning_component_year)

        learning_unit_year = learning_unit_component.learning_unit_year
        learning_unit_year.subtype = learning_unit_year_subtypes.PARTIM
        learning_unit_year.save()

        msg = learning_unit_deletion.delete_from_given_learning_unit_year(learning_unit_year)

        msg_success = _("%(subtype)s %(acronym)s has been deleted for the year %(year)s")
        self.assertEqual(msg_success % {'subtype': _('The partim'),
                                        'acronym': learning_unit_year.acronym,
                                        'year': learning_unit_year.academic_year},
                         msg.pop())

        self.assertEqual(LearningClassYear.objects.all().count(), 0)

        self.assertEqual(len(msg), number_classes)
        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitComponent.objects.get(id=learning_component_year.id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitComponent.objects.get(id=learning_unit_component.id)

        # The learning_unit_container won't be deleted because the learning_unit_year is a partim
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))

    def test_delete_learning_container_year(self):
        learning_container_year = LearningContainerYearFactory()

        learning_unit_year_full = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                          subtype=learning_unit_year_subtypes.FULL)
        learning_unit_year_partim = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                            subtype=learning_unit_year_subtypes.PARTIM)
        learning_unit_year_none = LearningUnitYearFactory(learning_container_year=learning_container_year,
                                                          subtype=None)

        learning_unit_deletion.delete_from_given_learning_unit_year(learning_unit_year_none)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_none.id)
        self.assertEqual(learning_unit_year_partim, LearningUnitYear.objects.get(id=learning_unit_year_partim.id))
        self.assertEqual(learning_unit_year_full, LearningUnitYear.objects.get(id=learning_unit_year_full.id))
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))

        learning_unit_deletion.delete_from_given_learning_unit_year(learning_unit_year_partim)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_partim.id)
        self.assertEqual(learning_unit_year_full, LearningUnitYear.objects.get(id=learning_unit_year_full.id))
        self.assertEqual(learning_container_year, LearningContainerYear.objects.get(id=learning_container_year.id))

        learning_unit_deletion.delete_from_given_learning_unit_year(learning_unit_year_full)

        with self.assertRaises(ObjectDoesNotExist):
            LearningUnitYear.objects.get(id=learning_unit_year_full.id)

        with self.assertRaises(ObjectDoesNotExist):
            LearningContainerYear.objects.get(id=learning_container_year.id)

    def test_check_delete_learning_unit_year_with_assistants(self):
        learning_unit_year = LearningUnitYearFactory()
        assistant_mandate = AssistantMandateFactory()
        tutoring = TutoringLearningUnitYear.objects.create(mandate=assistant_mandate,
                                                           learning_unit_year=learning_unit_year)

        msg = learning_unit_deletion.check_learning_unit_year_deletion(learning_unit_year)
        self.assertIn(tutoring, msg.keys())

    def test_can_delete_learning_unit_year_with_faculty_manager_role(self):
        # Faculty manager can only delete other type than COURSE/INTERNSHIP/DISSERTATION
        person = PersonFactory()
        add_to_group(person.user, learning_unit_deletion.FACULTY_MANAGER_GROUP)
        entity_version = EntityVersionFactory(entity_type=entity_type.FACULTY, acronym="SST",
                                              start_date=datetime.date(year=1990, month=1, day=1),
                                              end_date=None)
        PersonEntityFactory(person=person, entity=entity_version.entity, with_child=True)

        # Creation UE
        learning_unit = LearningUnitFactory()
        l_containeryear = LearningContainerYearFactory(academic_year=self.academic_year,
                                                       container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_containeryear, entity=entity_version.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        learning_unit_year = LearningUnitYearFactory(learning_unit=learning_unit,
                                                     academic_year=self.academic_year,
                                                     learning_container_year=l_containeryear,
                                                     subtype=learning_unit_year_subtypes.FULL)
        # Can remove FULL COURSE
        self.assertFalse(learning_unit_deletion.can_delete_learning_unit_year(person, learning_unit_year))

        # Can remove PARTIM COURSE
        learning_unit_year.subtype = learning_unit_year_subtypes.PARTIM
        learning_unit_year.save()
        self.assertTrue(learning_unit_deletion.can_delete_learning_unit_year(person, learning_unit_year))

        # With both role, greatest is taken
        add_to_group(person.user, learning_unit_deletion.CENTRAL_MANAGER_GROUP)
        learning_unit_year.subtype = learning_unit_year_subtypes.FULL
        learning_unit_year.save()
        self.assertTrue(learning_unit_deletion.can_delete_learning_unit_year(person, learning_unit_year))


def add_to_group(user, group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    group.user_set.add(user)
