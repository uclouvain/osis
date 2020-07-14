#!/usr/bin/env python
from django.core.management.base import BaseCommand

from base.models import entity_version
from base.models.education_group_year import EducationGroupYear
from base.models.learning_container_year import LearningContainerYear
from base.models.person_entity import PersonEntity


class Command(BaseCommand):
    def handle(self, *args, **options):
        # New entity
        elal_entity = entity_version.find("ELAL").entity_id

        # Entity to change entity
        lafr_entity = entity_version.find("LAFR").entity_id
        ling_entity = entity_version.find("LING").entity_id
        lmod_entity = entity_version.find("LMOD").entity_id
        mult_entity = entity_version.find("MULT").entity_id
        rom_entity = entity_version.find("ROM").entity_id
        thea_entity = entity_version.find("THEA").entity_id

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

    def add_person_entity(self, entities_to_change, new_entity):
        lines_to_add = PersonEntity.objects.filter(entity_id__in=entities_to_change)
        for line in lines_to_add:
            line.pk = None
            line.entity_id = new_entity
            line.save()


Command().handle()
