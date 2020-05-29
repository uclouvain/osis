import functools
import json
from collections import OrderedDict
from enum import Enum

from django.http import Http404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from base import models as mdl
from base.models.enums.education_group_types import GroupType
from education_group.forms.academic_year_choices import get_academic_year_choices
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.business_types import *
from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories import load_tree
from program_management.forms.custom_xls import CustomXlsForm
from program_management.models.element import Element
from program_management.serializers.program_tree_view import program_tree_view_serializer


class Tab(Enum):
    IDENTIFICATION = 0
    CONTENT = 1
    UTILIZATION = 2
    GENERAL_INFO = 3


class GroupRead(PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = 'base.view_educationgroup'
    raise_exception = True
    active_tab = None

    @functools.lru_cache()
    def get(self, request, *args, **kwargs):
        self.path = self.request.GET.get('path')
        if self.path is None:
            root_element = Element.objects.get(
                group_year__academic_year__year=self.kwargs['year'],
                group_year__partial_acronym=self.kwargs['code']
            )
            self.path = str(root_element.pk)
        return super().get(request, *args, **kwargs)

    @functools.lru_cache()
    def get_tree(self):
        root_element_id = self.path.split("|")[0]
        return load_tree.load(int(root_element_id))

    @cached_property
    def node_identity(self) -> 'NodeIdentity':
        return NodeIdentity(code=self.kwargs['code'], year=self.kwargs['year'])

    @functools.lru_cache()
    def get_object(self):
        return self.get_tree().get_node(self.path)

    def get_context_data(self, **kwargs):
        can_change_education_group = self.request.user.has_perm(
            'base.change_educationgroup',
            self.get_permission_object()
        )
        return {
            **super().get_context_data(**kwargs),
            "person": self.request.user.person,
            "enums": mdl.enums.education_group_categories,
            "can_change_education_group": can_change_education_group,
            "form_xls_custom": CustomXlsForm(),
            "tree": json.dumps(program_tree_view_serializer(self.get_tree())),
            "node": self.get_object(),
            "tab_urls": self.get_tab_urls(),
            "academic_year_choices": get_academic_year_choices(
                self.node_identity,
                self.path,
                _get_view_name_from_tab(self.active_tab),
            ),
            "group_year": self.get_group_year()  # TODO: Should be remove and use DDD object
        }

    @functools.lru_cache()
    def get_group_year(self):
        try:
            return GroupYear.objects.select_related('education_group_type', 'academic_year', 'management_entity')\
                                .get(academic_year__year=self.kwargs['year'], partial_acronym=self.kwargs['code'])
        except GroupYear.DoesNotExist:
            raise Http404

    def get_permission_object(self):
        return self.get_group_year()

    def get_tab_urls(self):
        node = self.get_object()
        return OrderedDict({
            Tab.IDENTIFICATION: {
                'text': _('Identification'),
                'active': Tab.IDENTIFICATION == self.active_tab,
                'display': True,
                'url': reverse('group_identification', args=[node.year, node.code]) + "?path={}".format(self.path)
            },
            Tab.CONTENT: {
                'text': _('Content'),
                'active': Tab.CONTENT == self.active_tab,
                'display': True,
                'url': reverse('group_content', args=[node.year, node.code]) + "?path={}".format(self.path),
            },
            Tab.UTILIZATION: {
                'text': _('Utilizations'),
                'active': Tab.UTILIZATION == self.active_tab,
                'display': True,
                'url': reverse('group_utilization', args=[node.year, node.code]) +
                "?path={}".format(self.path),
            },
            Tab.GENERAL_INFO: {
                'text': _('General informations'),
                'active': Tab.GENERAL_INFO == self.active_tab,
                'display': node.node_type == GroupType.COMMON_CORE,
                'url': reverse('group_general_information', args=[node.year, node.code]) +
                "?path={}".format(self.path),
            }
        })


def _get_view_name_from_tab(tab: Tab):
    return {
        Tab.IDENTIFICATION: 'group_identification',
        Tab.CONTENT: 'group_content',
        Tab.UTILIZATION: 'group_utilization',
        Tab.GENERAL_INFO: 'group_general_information',
    }[tab]


def _get_tab_urls(tab: Tab, node_identity: 'NodeIdentity', path: 'Path' = None) -> str:
    path = path or ""
    return reverse(
        _get_view_name_from_tab(tab),
        args=[node_identity.year, node_identity.code]
    ) + "?path={}".format(path)
