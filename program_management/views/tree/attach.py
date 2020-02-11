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
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.forms import formset_factory
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

from base.models.education_group_year import EducationGroupYear
from base.utils.cache import ElementCache
from base.views.common import display_warning_messages, display_success_messages
from base.views.mixins import AjaxTemplateMixin
from program_management.business.group_element_years import management
from program_management.ddd.domain import node
from program_management.ddd.repositories import fetch_tree
from program_management.forms.tree.attach import AttachNodeForm, AttachNodeFormSet
from program_management.models.enums.node_type import NodeType


class AttachNodeView(AjaxTemplateMixin, TemplateView):
    template_name = "tree/attach_inner.html"

    @cached_property
    def tree(self):
        root_id, *_ = self.request.GET['to_path'].split('|', 1)
        return fetch_tree.fetch(root_id)

    @cached_property
    def elements_to_attach(self):
        return management.fetch_elements_selected(self.request.GET, self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if 'to_path' not in request.GET:
            raise SuspiciousOperation('Missing to_path parameter')
        try:
            self.tree.get_node(request.GET['to_path'])
        except node.NodeNotFoundException:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_formset_class(self):
        return formset_factory(
            form=AttachNodeForm,
            formset=AttachNodeFormSet,
            extra=len(self.elements_to_attach)
        )

    def get_formset_kwargs(self):
        formset_kwargs = []
        for idx, element in enumerate(self.elements_to_attach):
            formset_kwargs.append({
                'node_id': element.pk,
                'node_type': NodeType.EDUCATION_GROUP.name if isinstance(element, EducationGroupYear) else
                NodeType.LEARNING_UNIT.name,
                'tree': self.tree,
                'to_path': self.request.GET['to_path']
            })
        return formset_kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.elements_to_attach:
            context_data['formset'] = kwargs.pop('formset', None) or self.get_formset_class()(
                form_kwargs=self.get_formset_kwargs()
            )
        else:
            display_warning_messages(self.request, _("Please cut or copy an item before attach it"))
        return context_data

    def post(self, request, *args, **kwargs):
        formset = self.get_formset_class()(self.request.POST or None, form_kwargs=self.get_formset_kwargs())
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        formset.save()
        ElementCache(self.request.user).clear()
        display_success_messages(
            self.request,
            _("The content of %(acronym)s has been updated.") % {
                "acronym": self.tree.get_node(self.request.GET['to_path']).acronym
            }
        )
        return None

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))
