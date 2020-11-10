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
import re
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count, Min, When, Case, Max
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, ngettext
from reversion.admin import VersionAdmin

from backoffice.settings.base import LANGUAGE_CODE_EN
from base.models import entity_version
from base.models.entity import Entity
from base.models.enums import academic_type, internship_presence, schedule_type, activity_presence, \
    diploma_printing_orientation, active_status, duration_unit, decree_category, rate_code
from base.models.enums import education_group_association
from base.models.enums import education_group_categories
from base.models.enums.education_group_types import MiniTrainingType, TrainingType, GroupType
from base.models.enums.funding_codes import FundingCodes
from base.models.enums.offer_enrollment_state import SUBSCRIBED, PROVISORY
from base.models.exceptions import ValidationWarning
from base.models.validation_rule import ValidationRule
from osis_common.models.serializable_model import SerializableModel, SerializableModelManager, SerializableModelAdmin, \
    SerializableQuerySet


class EducationGroupYearAdmin(VersionAdmin, SerializableModelAdmin):
    list_display = ('acronym', 'partial_acronym', 'title', 'academic_year', 'education_group_type', 'changed')
    list_filter = ('academic_year', 'education_group_type')
    raw_id_fields = (
        'education_group_type', 'academic_year',
        'education_group', 'enrollment_campus',
        'primary_language'
    )
    search_fields = ['acronym', 'partial_acronym', 'title', 'education_group__pk', 'id']

    actions = [
        'resend_messages_to_queue',
        'copy_reddot_data'
    ]

    def copy_reddot_data(self, request, queryset):
        # Potential circular imports
        from base.business.education_groups.automatic_postponement import ReddotEducationGroupAutomaticPostponement
        from base.views.common import display_success_messages, display_error_messages

        result, errors = ReddotEducationGroupAutomaticPostponement(queryset).postpone()
        count = len(result)
        display_success_messages(
            request, ngettext(
                "%(count)d education group has been updated with success.",
                "%(count)d education groups have been updated with success.", count
            ) % {'count': count}
        )
        if errors:
            display_error_messages(request, "{} : {}".format(
                _("The following education groups ended with error"),
                ", ".join([str(error) for error in errors])
            ))

    copy_reddot_data.short_description = _("Copy Reddot data from previous academic year.")


class EducationGroupYearQueryset(SerializableQuerySet):
    def get_queryset(self):
        return self.get_queryset().select_related('administration_entity',
                                                  'management_entity',
                                                  'management_entity_version')\
            .prefetch_related('administration_entity.entityversion_set',
                              'management_entity.entityversion_set')

    def get_nearest_years(self, year):
        return self.aggregate(
            futur=Min(
                Case(When(academic_year__year__gte=year, then='academic_year__year'))
            ),
            past=Max(
                Case(When(academic_year__year__lt=year, then='academic_year__year'))
            )
        )


class EducationGroupYearManager(SerializableModelManager):
    def get_queryset(self):
        return EducationGroupYearQueryset(self.model, using=self._db)

    def look_for_common(self, **kwargs):
        return self.filter(acronym__startswith='common', **kwargs)

    def get_common(self, **kwargs):
        return self.get(acronym='common', **kwargs)

    def get_nearest_years(self, year):
        return self.get_queryset().get_nearest_years(year)


class EducationGroupYear(SerializableModel):
    objects = EducationGroupYearManager()
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    acronym = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name=_("Acronym/Short title"),
    )

    title = models.CharField(
        max_length=240,
        verbose_name=_("Title in French")
    )

    title_english = models.CharField(
        max_length=240,
        blank=True,
        default="",
        verbose_name=_("Title in English")
    )

    partial_title = models.CharField(
        max_length=240,
        blank=True,
        null=True,
        default="",
        verbose_name=_("Partial title in French")
    )

    partial_title_english = models.CharField(
        max_length=240,
        blank=True,
        null=True,
        default="",
        verbose_name=_("Partial title in English")
    )

    academic_year = models.ForeignKey(
        'AcademicYear',
        verbose_name=_("validity"),
        on_delete=models.PROTECT
    )

    education_group = models.ForeignKey(
        'EducationGroup',
        on_delete=models.CASCADE
    )

    education_group_type = models.ForeignKey(
        'EducationGroupType',
        verbose_name=_("Type of training"),
        on_delete=models.CASCADE
    )

    active = models.CharField(
        max_length=20,
        choices=active_status.ACTIVE_STATUS_LIST,
        default=active_status.ACTIVE,
        verbose_name=_('Status')
    )

    partial_deliberation = models.BooleanField(
        default=False,
        verbose_name=_('Partial deliberation')
    )

    admission_exam = models.BooleanField(
        default=False,
        verbose_name=_('Admission exam')
    )

    funding = models.BooleanField(
        default=False,
        verbose_name=_('Funding')
    )

    funding_direction = models.CharField(
        max_length=1,
        blank=True,
        default="",
        choices=FundingCodes.choices(),
        verbose_name=_('Funding direction')
    )

    funding_cud = models.BooleanField(
        default=False,
        verbose_name=_('Funding international cooperation CCD/CUD')  # cud = commission universitaire au développement
    )

    funding_direction_cud = models.CharField(
        max_length=1,
        blank=True,
        default="",
        choices=FundingCodes.choices(),
        verbose_name=_('Funding international cooperation CCD/CUD direction')
    )

    academic_type = models.CharField(
        max_length=20,
        choices=academic_type.ACADEMIC_TYPES,
        blank=True,
        null=True,
        verbose_name=_('Academic type')
    )

    university_certificate = models.BooleanField(
        default=False,
        verbose_name=_('University certificate')
    )

    enrollment_campus = models.ForeignKey(
        'Campus',
        related_name='enrollment',
        blank=True,
        null=True,
        verbose_name=_("Enrollment campus"),
        on_delete=models.PROTECT
    )

    dissertation = models.BooleanField(
        default=False,
        verbose_name=_('dissertation')
    )

    internship = models.CharField(
        max_length=20,
        choices=internship_presence.INTERNSHIP_PRESENCE,
        default=internship_presence.NO,
        null=True,
        verbose_name=_('Internship')
    )

    schedule_type = models.CharField(
        max_length=20,
        choices=schedule_type.SCHEDULE_TYPES,
        default=schedule_type.DAILY,
        verbose_name=_('Schedule type')
    )

    english_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_("activities in English")
    )

    other_language_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_('Other languages activities')
    )

    other_campus_activities = models.CharField(
        max_length=20,
        choices=activity_presence.ACTIVITY_PRESENCES,
        blank=True,
        null=True,
        verbose_name=_('Activities on other campus')
    )

    professional_title = models.CharField(
        max_length=320,
        blank=True,
        default="",
        verbose_name=_('Professionnal title')
    )

    joint_diploma = models.BooleanField(default=False, verbose_name=_('Leads to diploma/certificate'))

    diploma_printing_orientation = models.CharField(
        max_length=30,
        choices=diploma_printing_orientation.DIPLOMA_FOCUS,
        blank=True,
        null=True
    )

    diploma_printing_title = models.CharField(
        max_length=240,
        blank=True,
        default="",
        verbose_name=_('Diploma title')
    )

    inter_organization_information = models.CharField(
        max_length=320,
        blank=True,
        default="",
    )

    inter_university_french_community = models.BooleanField(default=False)
    inter_university_belgium = models.BooleanField(default=False)
    inter_university_abroad = models.BooleanField(default=False)

    primary_language = models.ForeignKey(
        'reference.Language',
        null=True,
        verbose_name=_('Primary language'),
        on_delete=models.PROTECT
    )

    language_association = models.CharField(
        max_length=5,
        choices=education_group_association.EducationGroupAssociations.choices(),
        blank=True,
        null=True
    )

    keywords = models.CharField(
        max_length=320,
        blank=True,
        default="",
        verbose_name=_('Keywords')
    )

    duration = models.IntegerField(
        blank=True,
        null=True,
        default=1,  # We must set a default value for duration because duration_unit have a default value
        verbose_name=_('Duration'),
        validators=[MinValueValidator(1)]
    )

    duration_unit = models.CharField(
        max_length=40,
        choices=duration_unit.DURATION_UNIT,
        default=duration_unit.DurationUnits.QUADRIMESTER.value,
        blank=True,
        null=True,
        verbose_name=_('duration unit')
    )

    enrollment_enabled = models.BooleanField(
        default=True,
        verbose_name=_('Enrollment enabled')
    )

    partial_acronym = models.CharField(
        max_length=15,
        db_index=True,
        null=True,
        verbose_name=_("code"),
    )

    # TODO :: rename credits into expected_credits
    credits = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("credits"),
    )

    main_domain = models.ForeignKey(
        "reference.domain",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name=_("main domain")
    )

    secondary_domains = models.ManyToManyField(
        "reference.domain",
        through="EducationGroupYearDomain",
        related_name="education_group_years",
        verbose_name=_("secondary domains")
    )

    isced_domain = models.ForeignKey(
        "reference.DomainIsced",
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name=_("ISCED domain"),
        limit_choices_to={'is_ares': True},
    )

    management_entity = models.ForeignKey(
        Entity,
        verbose_name=_("Management entity"),
        null=True,
        related_name="management_entity",
        on_delete=models.PROTECT
    )

    administration_entity = models.ForeignKey(
        Entity, null=True,
        verbose_name=_("Administration entity"),
        related_name='administration_entity',
        on_delete=models.PROTECT
    )

    weighting = models.BooleanField(
        default=True,
        verbose_name=_('Weighting')
    )
    default_learning_unit_enrollment = models.BooleanField(
        default=False,
        verbose_name=_('Default learning unit enrollment')
    )

    languages = models.ManyToManyField(
        "reference.Language",
        through="EducationGroupLanguage",
        related_name="education_group_years"
    )

    decree_category = models.CharField(
        max_length=40,
        choices=decree_category.DecreeCategories.choices(),
        blank=True,
        null=True,
        verbose_name=_('Decree category')
    )

    rate_code = models.CharField(
        max_length=50,
        choices=rate_code.RATE_CODE,
        blank=True,
        null=True,
        verbose_name=_('Rate code')
    )

    internal_comment = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("comment (internal)"),
    )

    certificate_aims = models.ManyToManyField(
        "base.CertificateAim",
        through="EducationGroupCertificateAim",
        related_name="education_group_years",
        blank=True,
    )

    co_graduation = models.CharField(
        max_length=8,
        db_index=True,
        verbose_name=_("Code co-graduation inter CfB"),
        blank=True,
        null=True,
    )

    co_graduation_coefficient = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name=_('Co-graduation total coefficient'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )

    web_re_registration = models.BooleanField(
        default=True,
        verbose_name=_('Web re-registration'),
    )

    publication_contact_entity = models.ForeignKey(
        Entity,
        verbose_name=_("Publication contact entity"),
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    linked_with_epc = models.BooleanField(
        default=False,
        verbose_name=_('Linked with EPC')
    )

    class Meta:
        ordering = ("academic_year",)
        verbose_name = _("Education group year")
        unique_together = (
            ('education_group', 'academic_year'),
            ('partial_acronym', 'academic_year'),
            ('acronym', 'academic_year'),
        )
        index_together = [
            ("acronym", "academic_year"),
            ('partial_acronym', 'academic_year'),
        ]

    def __str__(self):
        return "{} - {} - {}".format(
            self.partial_acronym,
            self.acronym,
            self.academic_year,
        )

    @property
    def is_option(self):
        return self.education_group_type.name == MiniTrainingType.OPTION.name

    @property
    def is_finality(self):
        return self.education_group_type.name in TrainingType.finality_types()

    @property
    def is_continuing_education_education_group_year(self):
        return self.acronym.endswith('FC')

    @property
    def is_minor(self):
        return self.education_group_type.name in MiniTrainingType.minors()

    @property
    def is_major(self):
        return self.education_group_type.name == MiniTrainingType.FSA_SPECIALITY.name

    @property
    def is_deepening(self):
        return self.education_group_type.name == MiniTrainingType.DEEPENING.name

    @property
    def is_minor_major_option_list_choice(self):
        return self.education_group_type.name in GroupType.minor_major_option_list_choice()

    @property
    def is_common(self):
        return self.acronym.startswith('common')

    @property
    def is_main_common(self):
        return self.acronym == 'common'

    @property
    def is_a_master(self):
        return any([self.is_master60, self.is_master120, self.is_master180])

    @property
    def is_master120(self):
        return self.education_group_type.name == TrainingType.PGRM_MASTER_120.name

    @property
    def is_master60(self):
        return self.education_group_type.name == TrainingType.MASTER_M1.name

    @property
    def is_aggregation(self):
        return self.education_group_type.name == TrainingType.AGGREGATION.name

    @property
    def is_specialized_master(self):
        return self.education_group_type.name == TrainingType.MASTER_MC.name

    @property
    def is_bachelor(self):
        return self.education_group_type.name == TrainingType.BACHELOR.name

    @property
    def is_master180(self):
        return self.education_group_type.name == TrainingType.PGRM_MASTER_180_240.name

    @property
    def has_common_admission_condition(self):
        return any([self.is_bachelor, self.is_a_master, self.is_aggregation, self.is_specialized_master])

    @property
    def verbose(self):
        return "{} - {}".format(self.partial_acronym or "", self.acronym)

    @property
    def verbose_credit(self):
        title = self.title_english if self.title_english and translation.get_language() == LANGUAGE_CODE_EN \
            else self.title
        return "{} ({} {})".format(title, self.credits or 0, _("credits"))

    @property  # TODO :: move this into template tags or 'presentation' layer (not responsibility of model)
    def verbose_title(self):
        if self.is_finality:
            if self.partial_title_english and translation.get_language() == LANGUAGE_CODE_EN:
                return self.partial_title_english
            return self.partial_title
        else:
            if self.title_english and translation.get_language() == LANGUAGE_CODE_EN:
                return self.title_english
            return self.title

    @property
    def verbose_type(self):
        return self.education_group_type.get_name_display()

    @property
    def complete_title(self):
        return self.verbose_title

    def get_absolute_url(self):
        return reverse(
            'education_group_read_proxy',
            args=[self.academic_year.year, self.acronym]
        )

    @cached_property
    def administration_entity_version(self):
        return entity_version.find_entity_version_according_academic_year(
            self.administration_entity, self.academic_year
        )

    @cached_property
    def management_entity_version(self) -> Optional['entity_version.EntityVersion']:
        return entity_version.find_entity_version_according_academic_year(
            self.management_entity, self.academic_year
        )

    @cached_property
    def publication_contact_entity_version(self):
        if self.publication_contact_entity:
            return entity_version.find_entity_version_according_academic_year(
                self.publication_contact_entity, self.academic_year
            )
        return None

    @cached_property
    def coorganizations(self):
        return self.educationgrouporganization_set.all().order_by('all_students')

    def is_training(self):
        return self.education_group_type.category == education_group_categories.TRAINING

    def is_mini_training(self):
        return self.education_group_type.category == education_group_categories.MINI_TRAINING

    def delete(self, using=None, keep_parents=False):
        result = super().delete(using, keep_parents)

        # If the education_group has no more children, we can delete it
        if not self.education_group.educationgroupyear_set.all().exists():
            result = self.education_group.delete()
        return result

    @property
    def category(self):
        return self.education_group_type.category

    def clean(self):
        self.clean_academic_year()
        self.clean_acronym()
        self.clean_partial_acronym()
        self.clean_duration_data()

    def clean_academic_year(self):
        if self.academic_year.year < settings.YEAR_LIMIT_EDG_MODIFICATION:
            raise ValidationError({
                'academic_year': _("You cannot create/update an education group before %(limit_year)s") % {
                                "limit_year": settings.YEAR_LIMIT_EDG_MODIFICATION}
            })

    def clean_duration_data(self):
        if self.duration_unit is not None and self.duration is None:
            raise ValidationError({'duration': _("This field is required.")})
        elif self.duration is not None and self.duration_unit is None:
            raise ValidationError({'duration_unit': _("This field is required.")})

    @staticmethod
    def format_year_to_academic_year(year):
        return "{}-{}".format(str(year), str(year + 1)[-2:])

    def clean_partial_acronym(self, raise_warnings=False):
        if not self.partial_acronym:
            return

        egy_using_same_partial_acronym = EducationGroupYear.objects. \
            filter(partial_acronym=self.partial_acronym.upper()). \
            exclude(education_group=self.education_group_id). \
            get_nearest_years(self.academic_year.year)

        if egy_using_same_partial_acronym["futur"]:
            raise ValidationError({
                'partial_acronym': _("Partial acronym already exists in %(academic_year)s") % {
                    "academic_year": self.format_year_to_academic_year(egy_using_same_partial_acronym["futur"])
                }
            })

        my_validation_rule = self.rules.get('partial_acronym')
        if my_validation_rule and not bool(re.match(my_validation_rule.regex_rule, self.partial_acronym)):
            raise ValidationError({
                'partial_acronym': _("Partial acronym is invalid")
            })

        if raise_warnings and egy_using_same_partial_acronym["past"]:
            raise ValidationWarning({
                'partial_acronym': _("Partial acronym existed in %(academic_year)s") % {
                    "academic_year": self.format_year_to_academic_year(egy_using_same_partial_acronym["past"])
                }
            })

    def clean_acronym(self, raise_warnings=False):
        if not self.acronym:
            return

        egy_using_same_acronym = EducationGroupYear.objects. \
            filter(acronym=self.acronym.upper()).exclude(education_group=self.education_group_id)

        # Groups can reuse acronym of other groups
        if self.education_group_type.category == education_group_categories.GROUP:
            egy_using_same_acronym = egy_using_same_acronym. \
                exclude(education_group_type__category=education_group_categories.GROUP)

        egy_using_same_acronym = egy_using_same_acronym.get_nearest_years(self.academic_year.year)

        if egy_using_same_acronym["futur"]:
            raise ValidationError({
                'acronym': _("Acronym already exists in %(academic_year)s") % {
                    "academic_year": self.format_year_to_academic_year(egy_using_same_acronym["futur"])
                }
            })

        my_validation_rule = self.rules.get('acronym')
        if my_validation_rule and not bool(re.match(my_validation_rule.regex_rule, self.acronym)):
            raise ValidationError({
                'acronym': _("Acronym is invalid")
            })

        if raise_warnings and egy_using_same_acronym["past"]:
            raise ValidationWarning({
                'acronym': _("Acronym existed in %(academic_year)s") % {
                    "academic_year": self.format_year_to_academic_year(egy_using_same_acronym["past"])
                }
            })

    @property
    def rules(self):
        result = {}
        bulk_rules = ValidationRule.objects.in_bulk()
        for name in dir(self):
            field_ref = self.field_reference(name)
            if field_ref in bulk_rules:
                result[name] = bulk_rules[self.field_reference(name)]
        return result

    def field_reference(self, name):
        return self._field_reference(self._meta.model, name, self.education_group_type.external_id or 'osis')

    @staticmethod
    def _field_reference(model, name, *args):
        return '.'.join([model._meta.db_table, name, *args])

    def next_year(self):
        try:
            return self.education_group.educationgroupyear_set.get(academic_year__year=(self.academic_year.year + 1))
        except EducationGroupYear.DoesNotExist:
            return None

    def previous_year(self):
        try:
            return self.education_group.educationgroupyear_set.get(academic_year__year=(self.academic_year.year - 1))
        except EducationGroupYear.DoesNotExist:
            return None


def have_link_with_epc(acronym: str, year: int) -> bool:
    return EducationGroupYear.objects.filter(
        acronym=acronym,
        academic_year__year=year,
        linked_with_epc=True
    ).exists()


# TODO :: Annotate/Count() in only 1 query instead of 2
# TODO :: Count() on category_type == MINI_TRAINING will be in the future in another field FK (or other table).
def find_with_enrollments_count(learning_unit_year):
    education_groups_years = _find_with_learning_unit_enrollment_count(learning_unit_year)
    count_by_id = _count_education_group_enrollments_by_id(education_groups_years)
    for educ_group in education_groups_years:
        educ_group.count_formation_enrollments = count_by_id.get(educ_group.id) or 0
    return education_groups_years


def _count_education_group_enrollments_by_id(education_groups_years):
    educ_groups = EducationGroupYear.objects.filter(
        pk__in=[educ_group.id for educ_group in education_groups_years],
        offerenrollment__enrollment_state__in=[SUBSCRIBED, PROVISORY]
    ).annotate(
        count_formation_enrollments=Count('offerenrollment')
    ).values('id', 'count_formation_enrollments')
    return {obj['id']: obj['count_formation_enrollments'] for obj in educ_groups}


def _find_with_learning_unit_enrollment_count(learning_unit_year):
    return EducationGroupYear.objects \
        .filter(offerenrollment__learningunitenrollment__learning_unit_year_id=learning_unit_year) \
        .annotate(count_learning_unit_enrollments=Count('offerenrollment__learningunitenrollment')).order_by('acronym')
