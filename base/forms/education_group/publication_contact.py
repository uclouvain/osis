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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.exceptions import ImproperlyConfigured

from base.models.education_group_publication_contact import EducationGroupPublicationContact, ROLE_REQUIRED_FOR_TYPES


class EducationGroupPublicationContactForm(forms.ModelForm):
    class Meta:
        model = EducationGroupPublicationContact
        fields = ["type", "email", "description", "role_fr", "role_en"]

    def __init__(self, education_group_year=None, *args, **kwargs):
        if not education_group_year and not kwargs.get('instance'):
            raise ImproperlyConfigured("Provide an education_group_year or an instance")

        super().__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.instance.education_group_year = education_group_year
        self._disable_fields()

    @property
    def title(self):
        if self.instance.pk:
            return _('Update contact')
        return _('Create contact')

    def _disable_fields(self):
        self.fields['description'].disabled = True
        if self.instance.type not in ROLE_REQUIRED_FOR_TYPES:
            self.fields['role_fr'].disabled = self.fields['role_en'].disabled = True

        if self.instance.pk:
            self.fields['type'].disabled = True
