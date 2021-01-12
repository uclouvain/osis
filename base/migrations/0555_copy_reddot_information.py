import datetime
import logging
from typing import Type, Tuple, Iterable, Union

from django.conf import settings
from django.db import migrations
from django.db import models, IntegrityError

from base.models.admission_condition import AdmissionCondition, AdmissionConditionLine
from base.models.education_group_achievement import EducationGroupAchievement
from base.models.education_group_detailed_achievement import EducationGroupDetailedAchievement
from base.models.education_group_publication_contact import EducationGroupPublicationContact
from base.models.education_group_year import EducationGroupYear
from cms.enums.entity_name import OFFER_YEAR, GROUP_YEAR
from cms.models.translated_text import TranslatedText
from education_group.models.group_year import GroupYear

logger = logging.getLogger(settings.DEFAULT_LOGGER)
FROM_YEAR = 2021


def copy_reddot_information():
    copy_reddot_information_from_group_year()
    copy_reddot_information_from_education_group_year()


def copy_reddot_information_from_group_year():
    logger.info("Start Copy of reddot information from Group Years (year = {}) to last existing".format(FROM_YEAR))
    start_time = datetime.datetime.now()
    group_years = GroupYear.objects.filter(
        academic_year__year=FROM_YEAR
    )
    for group_year in group_years:
        next_group_years = GroupYear.objects.filter(
            group=group_year.group,
            academic_year__year__gt=group_year.academic_year.year
        )
        translated_texts = TranslatedText.objects.filter(
            entity=GROUP_YEAR,
            reference=group_year.id
        )
        for next_group_year in next_group_years:
            copy_general_information(translated_texts, next_group_year)
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    logger.info("Time to copy all cms : {}".format(total_time))


def copy_reddot_information_from_education_group_year():
    logger.info(
        "Start Copy of reddot information from Education Group Years (year = {}) to last existing".format(FROM_YEAR)
    )
    start_time = datetime.datetime.now()
    egys = EducationGroupYear.objects.filter(
        academic_year__year=FROM_YEAR
    )
    for egy in egys:
        next_egys = EducationGroupYear.objects.filter(
            education_group=egy.education_group,
            academic_year__year__gt=egy.academic_year.year
        )
        for next_egy in next_egys:
            copy_egy = CopyEgyOldModel(old_education_group_year=egy, new_education_group_year=next_egy)
            copy_egy.run()
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    logger.info("Time to copy all admission condition, publication contact and achievements : {}".format(total_time))


def copy_general_information(
        old_translated_texts: Iterable[TranslatedText], new_object: Union[GroupYear, EducationGroupYear]
):
    for translated_text in old_translated_texts:
        try:
            new_translated_text, _ = TranslatedText.objects.update_or_create(
                entity=OFFER_YEAR if isinstance(new_object, EducationGroupYear) else GROUP_YEAR,
                reference=new_object.id,
                language=translated_text.language,
                text_label=translated_text.text_label,
                defaults={
                    "text": translated_text.text
                }
            )
        except IntegrityError as e:
            logger.error(e.args)


class CopyEgyOldModel:

    def __init__(self, old_education_group_year: EducationGroupYear, new_education_group_year: EducationGroupYear):
        self.old_education_group_year = old_education_group_year
        self.new_education_group_year = new_education_group_year

    def run(self):
        self.copy_education_group_achievement()
        self.copy_data_from_model(EducationGroupPublicationContact, ('education_group_year', 'type', 'order'))
        self.copy_admission_condition()
        translated_texts = TranslatedText.objects.filter(
            entity=OFFER_YEAR,
            reference=self.old_education_group_year.id
        )
        copy_general_information(translated_texts, self.new_education_group_year)

    @staticmethod
    def copy_education_group_detailed_achievement(
            old_egy_detailed_achievements: Iterable[EducationGroupDetailedAchievement],
            new_old_education_group_achievement: EducationGroupAchievement
    ):
        for egyda in old_egy_detailed_achievements:
            try:
                new_egya, _ = EducationGroupDetailedAchievement.objects.update_or_create(
                    education_group_achievement=new_old_education_group_achievement,
                    order=egyda.order,
                    defaults={
                        "english_text": egyda.english_text,
                        "french_text": egyda.french_text,
                        "code_name": egyda.code_name
                    }

                )
            except IntegrityError as e:
                logger.error(e.args)

    def copy_education_group_achievement(self):
        old_egy_achievements = EducationGroupAchievement.objects.filter(
            education_group_year=self.old_education_group_year
        )
        for egya in old_egy_achievements:
            new_egya, _ = EducationGroupAchievement.objects.update_or_create(
                education_group_year=self.new_education_group_year,
                order=egya.order,
                defaults={
                    "english_text": egya.english_text,
                    "french_text": egya.french_text,
                    "code_name": egya.code_name,
                }

            )
            old_egy_detailed_achievements = EducationGroupDetailedAchievement.objects.filter(
                education_group_achievement_id=egya.id
            )
            self.copy_education_group_detailed_achievement(old_egy_detailed_achievements, new_egya)

    def copy_data_from_model(self, model: Type[models.Model], unique_fields: Tuple):
        result = []
        old_datas = model.objects.filter(
            education_group_year=self.old_education_group_year
        )
        model_fields = {field.name for field in model._meta._get_fields(reverse=False, include_hidden=True)}
        fields_to_update = model_fields - {"external_id", "changed", "id", 'uuid'}

        for old_data in old_datas:
            defaults = {field: getattr(old_data, field) for field in fields_to_update if field not in unique_fields}
            keys = {field: getattr(old_data, field) for field in unique_fields}
            keys["education_group_year"] = self.new_education_group_year
            try:
                new_data, created = model.objects.update_or_create(**keys, defaults=defaults)
            except (IntegrityError,) as e:
                logger.error(e.args)
                new_data = None
            result.append({'new': new_data, 'old': old_data})
        return result

    def copy_admission_condition(self):
        admission_list = self.copy_data_from_model(AdmissionCondition, ('education_group_year',))
        for admission in admission_list:
            old_lines = AdmissionConditionLine.objects.filter(admission_condition=admission['old'])
            for line in old_lines:
                try:
                    new_line, _ = AdmissionConditionLine.objects.update_or_create(
                        admission_condition=admission['new'],
                        section=line.section,
                        order=line.order,
                        defaults={
                            "access": line.access,
                            "diploma": line.diploma,
                            "conditions": line.conditions,
                            "remarks": line.remarks,
                            "diploma_en": line.diploma_en,
                            "conditions_en": line.conditions_en,
                            "remarks_en": line.remarks_en,
                        }
                    )
                except (IntegrityError, AdmissionConditionLine.MultipleObjectsReturned) as e:
                    logger.error(e.args)


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0554_remove_in_charge'),
    ]

    operations = [
        migrations.RunPython(copy_reddot_information),
    ]
