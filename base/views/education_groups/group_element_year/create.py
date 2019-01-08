############################################################################
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
############################################################################
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

from base.business.group_element_years.management import SELECT_CACHE_KEY, extract_child_from_cache
from base.forms.education_group.group_element_year import GroupElementYearForm, GroupElementYearMinorMajorOptionForm
from base.models.enums.education_group_types import GroupType
from base.models.exceptions import IncompatiblesTypesException, MaxChildrenReachedException
from base.utils.cache import cache
from base.views.common import display_warning_messages
from base.views.education_groups.group_element_year.common import GenericGroupElementYearMixin


class CreateGroupElementYearView(GenericGroupElementYearMixin, CreateView):
    # CreateView
    template_name = "education_group/group_element_year_comment_inner.html"

    def get_form_class(self):
        is_minor_major_option = self.education_group_year.education_group_type.name in GroupType.minor_major_option()
        return GroupElementYearMinorMajorOptionForm if is_minor_major_option else GroupElementYearForm

    def get_form_kwargs(self):
        """ For the creation, the group_element_year needs a parent and a child """
        kwargs = super().get_form_kwargs()

        try:
            selected_data = cache.get(SELECT_CACHE_KEY)
            cached_data = extract_child_from_cache(self.education_group_year, selected_data)
            if not cached_data:
                raise ObjectDoesNotExist
            kwargs.update({
                'parent': self.education_group_year,
                'child_branch': cached_data.get('child_branch'),
                'child_leaf': cached_data.get('child_leaf')
            })

        except ObjectDoesNotExist:
            warning_msg = _("Please Select or Move an item before Attach it")
            display_warning_messages(self.request, warning_msg)

        except (IncompatiblesTypesException, MaxChildrenReachedException) as e:
            warning_msg = e.errors
            display_warning_messages(self.request, warning_msg)

        except IntegrityError as e:
            warning_msg = str(e)
            display_warning_messages(self.request, warning_msg)

        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        # Clear cache.
        cache.set(SELECT_CACHE_KEY, None, timeout=None)
        return super().form_valid(form)

    # SuccessMessageMixin
    def get_success_message(self, cleaned_data):
        return _("The link of %(acronym)s has been created") % {'acronym': self.object.child}

    def get_success_url(self):
        """ We'll reload the page """
        return
