from django import forms
from django.forms import formset_factory

from base.forms.utils import choice_field
from base.models.enums.link_type import LinkTypes


class LinkForm(forms.Form):
    relative_credits = forms.IntegerField(required=False)
    is_mandatory = forms.BooleanField()
    link_type = forms.ChoiceField(choices=choice_field.add_blank(LinkTypes.choices()), required=False)
    block = forms.CharField(required=False)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    comment_english = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))


ContentFormSet = formset_factory(LinkForm, extra=0)
