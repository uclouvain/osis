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
from django import forms
from django.utils.translation import gettext as _

from base.business.group_element_years.management import is_max_child_reached
from base.models.enums import education_group_categories
from base.models.enums.link_type import LinkTypes
from base.models.group_element_year import GroupElementYear


class GroupElementYearForm(forms.ModelForm):
    class Meta:
        model = GroupElementYear
        fields = [
            "relative_credits",
            "is_mandatory",
            "block",
            "quadrimester_derogation",
            "link_type",
            "comment",
            "comment_english",
            "access_condition"
        ]
        widgets = {
            "comment": forms.Textarea(attrs={'rows': 5}),
            "comment_english": forms.Textarea(attrs={'rows': 5}),

        }

    def __init__(self, *args, parent=None, child_branch=None, child_leaf=None, **kwargs):
        super().__init__(*args, **kwargs)

        # No need to attach FK to an existing GroupElementYear
        if not self.instance.pk:
            self.instance.parent = parent
            self.instance.child_leaf = child_leaf
            self.instance.child_branch = child_branch

        if self.instance.parent:
            self._define_fields()

    def _define_fields(self):
        if self.instance.child_branch and not self._check_authorized_relationship(
                self.instance.child_branch.education_group_type):
            self.fields.pop("access_condition")

            # Change the initial but (for strange reasons) let the possibility to the user to try with the main link.
            # Like that he will see the form error.
            self.fields["link_type"].initial = LinkTypes.REFERENCE.name

        elif self._is_education_group_year_a_minor_major_option_list_choice(self.instance.parent) and \
                not self._is_education_group_year_a_minor_major_option_list_choice(self.instance.child_branch):
            self._keep_only_fields(["access_condition"])

        elif self.instance.parent.education_group_type.category == education_group_categories.TRAINING and \
                self._is_education_group_year_a_minor_major_option_list_choice(self.instance.child_branch):
            self._keep_only_fields(["block"])

        else:
            self.fields.pop("access_condition")

    def save(self, commit=True):
        obj = super().save(commit)
        if self._is_education_group_year_a_minor_major_option_list_choice(obj.parent):
            self._reorder_children_by_partial_acronym(obj.parent)
        return obj

    def clean_link_type(self):
        """
        All of these controls only work with child branch.
        The validation with learning_units (child_leaf) is in the model.
        """
        data_cleaned = self.cleaned_data.get('link_type')

        if self.instance.child_branch:
            if data_cleaned == LinkTypes.REFERENCE.name:
                self._clean_link_type_reference()
            else:
                self._clean_link_type_main()
        return data_cleaned

    def _clean_link_type_main(self):
        parent_type = self.instance.parent.education_group_type

        # For the main link,  we have to check if the parent type is compatible with its child's type
        child = self.instance.child_branch
        if not self._check_authorized_relationship(child.education_group_type):
            raise forms.ValidationError(
                _("You cannot attach \"%(child)s\" (type \"%(child_type)s\") to \"%(parent)s\" (type "
                  "\"%(parent_type)s\")") % {
                    'child': child,
                    'child_type': child.education_group_type,
                    'parent': self.instance.parent,
                    'parent_type': parent_type,
                }
            )

    def _clean_link_type_reference(self):
        parent_type = self.instance.parent.education_group_type

        # All types of children are allowed for the reference link but we must check the type of grandchildren
        for ref_group in self.instance.child_branch.children_group_element_years:
            ref_child_type = ref_group.child_branch.education_group_type

            if not self._check_authorized_relationship(ref_child_type):
                raise forms.ValidationError(
                    _("You are not allow to create a reference link between a %(parent_type)s and a %(child_type)s."
                      ) % {
                        "parent_type": parent_type,
                        "child_type": ref_child_type,
                    })

            # We have to check if the max limit is reached for all grandchildren
            if is_max_child_reached(self.instance.parent, ref_child_type):
                raise forms.ValidationError(
                    _("The number of children of type \"%(child_type)s\" for \"%(parent)s\" has already reached the "
                      "limit.") % {
                        'child_type': ref_child_type,
                        'parent': self.instance.parent
                    }
                )

    def _check_authorized_relationship(self, child_type):
        return self.instance.parent.education_group_type.authorized_parent_type.filter(child_type=child_type).exists()

    @staticmethod
    def _reorder_children_by_partial_acronym(parent):
        children = parent.children.order_by("child_branch__partial_acronym")

        for counter, child in enumerate(children):
            child.order = counter
            child.save()

    def _keep_only_fields(self, fields_to_keep):
        self.fields = {name: field for name, field in self.fields.items() if name in fields_to_keep}

    @staticmethod
    def _is_education_group_year_a_minor_major_option_list_choice(egy):
        return egy.is_minor_major_option_list_choice if egy else False
