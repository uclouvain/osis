##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django import forms
from django.utils.translation import gettext_lazy

from assessments.models.score_sheet_address import ScoreSheetAddress
from reference.models.country import Country


class ScoreSheetAddressForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, label=gettext_lazy('Country'))
    recipient = forms.CharField(max_length=255, label=gettext_lazy('Recipient'))
    location = forms.CharField(max_length=255, label=gettext_lazy('Location'))
    postal_code = forms.CharField(max_length=255, label=gettext_lazy('Postal code'))
    city = forms.CharField(max_length=255, label=gettext_lazy('City'))
    offer_year = forms.CharField()
    email = forms.EmailField(required=False)

    class Meta:
        model = ScoreSheetAddress
        exclude = ['external_id', 'changed']
