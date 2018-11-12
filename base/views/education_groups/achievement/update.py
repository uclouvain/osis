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
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, UpdateView

from base.business.education_groups.perms import is_eligible_to_change_achievement
from base.forms.education_group.achievement import ActionForm, EducationGroupAchievementForm, \
    EducationGroupDetailedAchievementForm
from base.views.common import display_error_messages
from base.views.education_groups.achievement.common import EducationGroupAchievementMixin, \
    EducationGroupDetailedAchievementMixin
from base.views.mixins import AjaxTemplateMixin


class EducationGroupAchievementAction(EducationGroupAchievementMixin, FormView):
    form_class = ActionForm
    http_method_names = ('post',)
    rules = [is_eligible_to_change_achievement]

    def form_valid(self, form):
        if form.cleaned_data['action'] == 'up':
            self.get_object().up()
        elif form.cleaned_data['action'] == 'down':
            self.get_object().down()
        return super().form_valid(form)

    def form_invalid(self, form):
        display_error_messages(self.request, _("Invalid action"))
        return HttpResponseRedirect(self.get_success_url())


class UpdateEducationGroupAchievement(AjaxTemplateMixin, EducationGroupAchievementMixin, UpdateView):
    template_name = "education_group/blocks/form/update_achievement.html"
    form_class = EducationGroupAchievementForm
    rules = [is_eligible_to_change_achievement]


class UpdateEducationGroupDetailedAchievement(EducationGroupDetailedAchievementMixin, UpdateEducationGroupAchievement):
    form_class = EducationGroupDetailedAchievementForm


class EducationGroupDetailedAchievementAction(EducationGroupDetailedAchievementMixin, EducationGroupAchievementAction):
    pass
