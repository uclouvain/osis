#!/usr/bin/env python
from django.db.models import Q
from django.utils import timezone

from django.core.management.base import BaseCommand

from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.learning_container_year import LearningContainerYear
from base.models.person_entity import PersonEntity


class Command(BaseCommand):
    def handle(self, *args, **options):
        date = timezone.now()
        # New entity
        elal_entity = EntityVersion.objects.current(date).get(acronym="ELAL").entity_id

        # Entity to change entity
        lafr_entity = EntityVersion.objects.current(date).get(acronym="LAFR").entity_id
        ling_entity = EntityVersion.objects.current(date).get(acronym="LING").entity_id
        lmod_entity = EntityVersion.objects.current(date).get(acronym="LMOD").entity_id
        mult_entity = EntityVersion.objects.current(date).get(acronym="MULT").entity_id
        rom_entity = EntityVersion.objects.current(date).get(acronym="ROM").entity_id
        thea_entity = EntityVersion.objects.current(date).get(acronym="THEA").entity_id

        self.modify_education_group(
            [lafr_entity, ling_entity, lmod_entity, mult_entity, rom_entity, thea_entity],
            elal_entity
        )
        self.modify_learning_unit(
            [lafr_entity, ling_entity, lmod_entity, mult_entity, rom_entity, thea_entity],
            elal_entity
        )
        self.add_person_entity(
            [lafr_entity, ling_entity, lmod_entity, mult_entity, rom_entity, thea_entity],
            elal_entity
        )

    def modify_education_group(self, entities_to_change, new_entity):
        EducationGroupYear.objects.filter(
            academic_year__year__gte=2020,
            management_entity_id__in=entities_to_change
        ).update(
            management_entity_id=new_entity
        )

        EducationGroupYear.objects.filter(
            academic_year__year__gte=2020,
            administration_entity__in=entities_to_change
        ).update(
            administration_entity_id=new_entity
        )

        # Update for changed
        qs = EducationGroupYear.objects.filter(
            Q(management_entity_id=new_entity) | Q(administration_entity_id=new_entity)
        )
        for elem in qs:
            elem.save()

    def modify_learning_unit(self, entities_to_change, new_entity):
        LearningContainerYear.objects.filter(
            academic_year__year__gte=2020,
            requirement_entity__in=entities_to_change
        ).update(
            requirement_entity_id=new_entity
        )
        LearningContainerYear.objects.filter(
            academic_year__year__gte=2020,
            allocation_entity__in=entities_to_change
        ).update(
            allocation_entity_id=new_entity
        )
        LearningContainerYear.objects.filter(
            academic_year__year__gte=2020,
            additional_entity_1__in=entities_to_change
        ).update(
            additional_entity_1_id=new_entity
        )
        LearningContainerYear.objects.filter(
            academic_year__year__gte=2020,
            additional_entity_2__in=entities_to_change
        ).update(
            additional_entity_2_id=new_entity
        )

        # Update for changed
        qs = LearningContainerYear.objects.filter(
            Q(requirement_entity_id=new_entity) | Q(allocation_entity_id=new_entity) |
            Q(additional_entity_1_id=new_entity) | Q(additional_entity_2_id=new_entity)
        )
        for elem in qs:
            elem.save()

    def add_person_entity(self, entities_to_change, new_entity):
        lines_to_add = PersonEntity.objects.filter(entity_id__in=entities_to_change)
        for line in lines_to_add:
            if not PersonEntity.objects.filter(
                entity_id=new_entity, person=line.person
            ).exists():
                line.pk = None
                line.entity_id = new_entity
                line.save()


Command().handle()
