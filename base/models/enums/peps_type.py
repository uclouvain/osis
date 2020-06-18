from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum


class PepsTypes(ChoiceEnum):
    NON_RENSEIGNE = _('Not defined')
    HTM = _('Disability')
    SPORT = _('Sport')
    ARTISTE = _('Artist')
    ENTREPRENARIAT = _('Entrepreneur')
    # TODO: Aménagement jury


class HtmSubtypes(ChoiceEnum):
    PMR = _('Person with reduced mobility')
    AUTRE_HTM = _('Other disability')


class SportSubtypes(ChoiceEnum):
    ESHN = _('High Level Promising athlete')
    ES = _('Promising athlete')
