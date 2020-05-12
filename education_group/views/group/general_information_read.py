from django.conf import settings
from django.db.models import OuterRef, F, Subquery, fields
from django.urls import reverse

from base.business.education_groups import general_information_sections
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from education_group.views.group.common_read import Tab, GroupRead


class GroupReadGeneralInformation(GroupRead):
    template_name = "group/general_informations_read.html"
    active_tab = Tab.GENERAL_INFO

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
