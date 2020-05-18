from django.db.models import F
from django.utils.translation import gettext_lazy as _

from base.models.admission_condition import AdmissionCondition


def get_admission_condition(acronym: str, year: int):
    try:
        admission_condition = AdmissionCondition.objects.filter(
            education_group_year__acronym=acronym,
            education_group_year__academic_year__year=year
        ).annotate(
            admission_requirements_fr=F('text_free'),
            admission_requirements_en=F('text_free_en'),
        ).values(
            'admission_requirements_fr',
            'admission_requirements_en'
        ).get()
    except AdmissionCondition.DoesNotExist:
        return __default_admission_condition()
    return __format_admission_condition(admission_condition)


def __format_admission_condition(admission_condition):
    admission_condition_formated = __default_admission_condition()
    admission_condition_formated['admission_requirements'].update({
        'text_fr': admission_condition['admission_requirements_fr'],
        'text_en': admission_condition['admission_requirements_en']
    })
    return admission_condition_formated


def __default_admission_condition():
    return {
        'admission_requirements': {
            'label_translated': _('Specific admission requirements'),
            'text_fr': '',
            'text_en': ''
        }
    }
