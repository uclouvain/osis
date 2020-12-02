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
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

import base.business.learning_unit
from attribution import models as mdl_attr
from base import models as mdl
from base.forms.my_message import MyMessageActionForm, MyMessageForm
from base.models.academic_year import starting_academic_year
from base.models.education_group_year import EducationGroupYear
from osis_common.models import message_history as message_history_mdl


@login_required
def my_osis_index(request):
    return render(request, "my_osis/home.html", {})


@login_required
def my_messages_index(request):
    person = mdl.person.find_by_user(request.user)
    my_messages = message_history_mdl.find_my_messages(person.id)
    my_messages_formset = None
    if not my_messages:
        messages.add_message(request, messages.INFO, _('No Messages'))
    else:
        my_messages_formset = get_messages_formset(my_messages)
    return render(request,
                  "my_osis/my_messages.html",
                  {
                      'my_messages_formset': my_messages_formset,
                      'my_message_action_form': MyMessageActionForm()
                  })


@login_required
def my_messages_action(request):
    my_message_action_form = MyMessageActionForm(request.POST)
    my_messages_formset = formset_factory(MyMessageForm)(request.POST, request.FILES)
    if my_message_action_form.is_valid() and my_messages_formset.is_valid():
        my_messages_ids_to_action = [mess_form.cleaned_data.get('id')
                                     for mess_form in my_messages_formset
                                     if mess_form.cleaned_data.get('selected')]
        if 'MARK_AS_READ' in my_message_action_form.cleaned_data.get('action'):
            message_history_mdl.mark_as_read(my_messages_ids_to_action)
        elif 'DELETE' in my_message_action_form.cleaned_data.get('action'):
            message_history_mdl.delete_my_messages(my_messages_ids_to_action)
    return HttpResponseRedirect(reverse('my_messages'))


@login_required
def delete_from_my_messages(request, message_id):
    message = message_history_mdl.find_by_id(message_id)
    person_user = mdl.person.find_by_user(request.user)
    if message and (message.receiver_person_id == person_user.id):
        message_history_mdl.delete_my_messages([message_id, ])
    return HttpResponseRedirect(reverse('my_messages'))


@login_required
def read_message(request, message_id):
    message = message_history_mdl.read_my_message(message_id)
    return render(request, "my_osis/my_message.html", {'my_message': message, })


@login_required
def profile(request):
    return render(request, "my_osis/profile.html", _get_data(request))


@login_required
def profile_lang(request):
    ui_language = request.POST.get('ui_language')
    mdl.person.change_language(request.user, ui_language)
    translation.activate(ui_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = ui_language
    return profile(request)


@login_required
def profile_lang_edit(request, ui_language):
    mdl.person.change_language(request.user, ui_language)
    translation.activate(ui_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = ui_language
    return redirect(request.META['HTTP_REFERER'])


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('osis_common.change_messagetemplate'))
def messages_templates_index(request):
    return HttpResponseRedirect(reverse('admin:base_messagetemplate_changelist'))


@login_required
def profile_attributions(request):
    data = _get_data(request)
    data.update({'tab_attribution_on': True})
    return render(request, "my_osis/profile.html", data)


@login_required
def _get_data(request):
    person = mdl.person.find_by_user(request.user)
    tutor = mdl.tutor.find_by_person(person)
    programs = base.auth.roles.program_manager.find_by_person(person).prefetch_related(
        Prefetch(
            'education_group__educationgroupyear_set',
            queryset=EducationGroupYear.objects.filter(
                academic_year=starting_academic_year()
            ).select_related('academic_year'),
            to_attr='current_egy'
        )
    ).order_by('education_group__educationgroupyear__acronym').distinct()

    return {'person': person,
            'addresses': mdl.person_address.find_by_person(person),
            'tutor': tutor,
            'attributions': mdl_attr.attribution.search(tutor=tutor) if tutor else None,
            'programs': programs,
            'supported_languages': settings.LANGUAGES,
            'default_language': settings.LANGUAGE_CODE,
            'summary_submission_opened': base.business.learning_unit.is_summary_submission_opened()}


def get_messages_formset(my_messages):
    initial_formset_content = [{'selected': False,
                                'subject': message_hist.subject,
                                'created': message_hist.created,
                                'id': message_hist.id,
                                'read': message_hist.read_by_user
                                } for message_hist in my_messages]
    return formset_factory(MyMessageForm, extra=0)(initial=initial_formset_content)
