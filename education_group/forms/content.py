from typing import Union

from django import forms
from django.forms import formset_factory, BaseFormSet

from base.forms.utils import choice_field
from base.models.enums.education_group_types import GroupType, TrainingType
from base.models.enums.link_type import LinkTypes
from education_group.ddd.domain.group import Group
from learning_unit.ddd.domain.learning_unit_year import LearningUnitYear


class LinkForm(forms.Form):
    relative_credits = forms.IntegerField(required=False, widget=forms.TextInput)
    is_mandatory = forms.BooleanField(required=False)
    access_condition = forms.BooleanField(required=False)
    link_type = forms.ChoiceField(choices=choice_field.add_blank(LinkTypes.choices()), required=False)
    block = forms.CharField(required=False)
    comment_fr = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))
    comment_en = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, parent_obj: Group = None, child_obj: Union[Group, LearningUnitYear] = None, **kwargs):
        self.parent_obj = parent_obj
        self.child_obj = child_obj
        super().__init__(*args, **kwargs)

        self.__initialize_fields()

    def __initialize_fields(self):
        if self.is_a_parent_minor_major_option_list_choice() and \
           not self.is_a_child_minor_major_option_list_choice():
            fields_to_exclude = (
                'relative_credits',
                'is_mandatory',
                'link_type',
                'block',
                'comment_fr',
                'comment_en',
            )
        elif self.is_a_child_minor_major_option_list_choice() and \
                self.parent_obj.type.name in TrainingType.get_names():
            fields_to_exclude = (
                'relative_credits',
                'is_mandatory',
                'link_type',
                'access_condition',
                'comment_fr',
                'comment_en',
            )
        elif self.is_a_link_with_child_of_learning_unit():
            fields_to_exclude = (
                'link_type',
                'access_condition',
            )
        else:
            fields_to_exclude = (
                'relative_credits',
                'access_condition',
            )
        [self.fields.pop(field_name) for field_name in fields_to_exclude]

    def is_a_link_with_child_of_learning_unit(self):
        return isinstance(self.child_obj, LearningUnitYear)

    def is_a_parent_minor_major_option_list_choice(self):
        return self.parent_obj and self.parent_obj.is_minor_major_option_list_choice()

    def is_a_child_minor_major_option_list_choice(self):
        return isinstance(self.child_obj, Group) and \
               self.child_obj.is_minor_major_option_list_choice()


class BaseContentFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        if self.form_kwargs:
            return self.form_kwargs[index]
        return {}


ContentFormSet = formset_factory(form=LinkForm, formset=BaseContentFormSet, extra=0)
