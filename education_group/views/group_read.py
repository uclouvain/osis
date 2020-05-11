import json
from enum import Enum

from django.conf import settings
from django.db.models import OuterRef, Subquery, fields, F
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from reversion.models import Version

from base import models as mdl
from base.business.education_groups import general_information_sections
from base.models.enums.education_group_types import GroupType
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.models.group_year import GroupYear
from osis_role.contrib.views import PermissionRequiredMixin
from program_management.ddd.repositories import load_tree
from program_management.ddd.service import tree_service
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

    def get(self, request, *args, **kwargs):
        self.path = self.request.GET.get('path')
        if self.path is None:
            root_element = Element.objects.get(
                group_year__academic_year__year=self.kwargs['year'],
                group_year__partial_acronym=self.kwargs['code']
            )
            self.path = str(root_element.pk)
        return super().get(request, *args, **kwargs)

    def get_tree(self):
        root_element_id = self.path.split("|")[0]
        return load_tree.load(int(root_element_id))

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
            "group_year": self.get_group_year()  # TODO: Should be remove and use DDD object
        }

    def get_group_year(self):
        return GroupYear.objects.select_related('education_group_type', 'academic_year', 'management_entity')\
                                .get(academic_year__year=self.kwargs['year'], partial_acronym=self.kwargs['code'])

    def get_permission_object(self):
        return self.get_group_year()

    def get_tab_urls(self):
        node = self.get_object()
        tabs = [
            {
                'text': _('Identification'),
                'active': False,
                'url': reverse('group_identification', args=[node.year, node.code]) + "?path={}".format(self.path)
            },
            {
                'text': _('Content'),
                'active': False,
                'url': reverse('group_content', args=[node.year, node.code]) + "?path={}".format(self.path),
            },
            {
                'text': _('Utilizations'),
                'active': False,
                'url': reverse('group_utilization', args=[node.year, node.code]) +
                "?path={}".format(self.path),
            },
        ]
        if node.node_type == GroupType.COMMON_CORE:
            tabs += [
                {
                    'text': _('General informations'),
                    'active': False,
                    'url': reverse('group_general_information', args=[node.year, node.code]) +
                    "?path={}".format(self.path),
                }
            ]
        return tabs


class GroupReadIdentification(GroupRead):
    template_name = "group/identification_read.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "versions": self.get_related_versions(),
        }

    def get_tab_urls(self):
        tab_urls = super().get_tab_urls()
        tab_urls[Tab.IDENTIFICATION.value]['active'] = True
        return tab_urls

    def get_related_versions(self):
        return Version.objects.none()


class GroupReadContent(GroupRead):
    template_name = "group/content_read.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "children": self.get_object().children
        }

    def get_tab_urls(self):
        tab_urls = super().get_tab_urls()
        tab_urls[Tab.CONTENT.value]['active'] = True
        return tab_urls


class GroupReadUsing(GroupRead):
    template_name = "group/utilization_read.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        node = self.get_object()
        trees = tree_service.search_trees_using_node(node)

        context['utilization_rows'] = []
        for tree in trees:
            context['utilization_rows'] += [
                {'link': link, 'root_nodes': [tree.root_node]}
                for link in tree.get_links_using_node(node)
            ]
        context['utilization_rows'] = sorted(context['utilization_rows'], key=lambda row: row['link'].parent.code)
        return context

    def get_tab_urls(self):
        tab_urls = super().get_tab_urls()
        tab_urls[Tab.UTILIZATION.value]['active'] = True
        return tab_urls


class GroupReadGeneralInformation(GroupRead):
    template_name = "group/general_informations_read.html"

    def get_context_data(self, **kwargs):
        node = self.get_object()
        return {
            **super().get_context_data(**kwargs),
            "labels": self.get_translated_labels(),
            "publish_url": reverse('publish_general_information', args=[node.year, node.code]) +
            "?path={}".format(self.path),
            "can_edit_information": self.request.user.has_perm("base.change_pedagogyinformation", self.get_group_year())
        }

    def get_translated_labels(self):
        subqstranslated_fr = TranslatedText.objects.filter(reference=self.get_object().pk, text_label=OuterRef('pk'),
                                                           language=settings.LANGUAGE_CODE_FR).values('text')[:1]
        subqstranslated_en = TranslatedText.objects.filter(reference=self.get_object().pk, text_label=OuterRef('pk'),
                                                           language=settings.LANGUAGE_CODE_EN).values('text')[:1]
        subqslabel = TranslatedTextLabel.objects.filter(
            text_label=OuterRef('pk'),
            language=self.request.LANGUAGE_CODE
        ).values('label')[:1]

        qs = TextLabel.objects.filter(
            label=general_information_sections.INTRODUCTION,
        ).annotate(
            label_id=F('label'),
            label_translated=Subquery(subqslabel, output_field=fields.CharField()),
            text_fr=Subquery(subqstranslated_fr, output_field=fields.CharField()),
            text_en=Subquery(subqstranslated_en, output_field=fields.CharField())
        ).values('label_id', 'label_translated', 'text_fr', 'text_en')
        return qs

    def get_tab_urls(self):
        tab_urls = super().get_tab_urls()
        tab_urls[Tab.GENERAL_INFO.value]['active'] = True
        return tab_urls
