import functools
from typing import Dict, List, Union

from django.http import Http404
from django.shortcuts import render
from django.utils.functional import cached_property
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from base.models import learning_unit_year
from learning_unit.ddd.business_types import *
from learning_unit.ddd import command as command_learning_unit_year
from learning_unit.ddd.service.read import get_multiple_learning_unit_years_service

from osis_role.contrib.views import PermissionRequiredMixin

from education_group.ddd.business_types import *
from education_group.ddd import command as command_education_group
from education_group.ddd.domain.exception import TrainingNotFoundException
from education_group.ddd.service.read import get_training_service

from program_management.ddd.business_types import *
from program_management.ddd import command
from program_management.ddd.service.read import get_program_tree_version_from_node_service
from program_management.forms import version


class TrainingVersionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.change_educationgroup'
    raise_exception = True

    template_name = "tree_version/training_version_update.html"

    def get(self, request, *args, **kwargs):
        context = {
            "training_version_form": self.training_version_form,
        }
        return render(request, self.template_name, context)

    @cached_property
    def training_version_form(self) -> 'version.UpdateTrainingVersionForm':
        training_identity = self.get_training_obj().entity_id
        node_identity = self.get_program_tree_obj().root_node.entity_id
        return version.UpdateTrainingVersionForm(
            self.request.POST or None,
            training_identity=training_identity,
            node_identity=node_identity,
            initial=self._get_training_version_form_initial_values()
        )

    @functools.lru_cache()
    def get_training_obj(self) -> 'Training':
        try:
            get_cmd = command_education_group.GetTrainingCommand(
                acronym=self.kwargs["title"],
                year=int(self.kwargs["year"])
            )
            return get_training_service.get_training(get_cmd)
        except TrainingNotFoundException:
            raise Http404

    @functools.lru_cache()
    def get_program_tree_version_obj(self) -> 'ProgramTreeVersion':
        get_cmd = command.GetProgramTreeVersionFromNodeCommand(
            code=self.kwargs['code'],
            year=self.kwargs['year']
        )
        return get_program_tree_version_from_node_service.get_program_tree_version_from_node(get_cmd)

    @functools.lru_cache()
    def get_program_tree_obj(self) -> 'ProgramTree':
        return self.get_program_tree_version_obj().get_tree()

    def _get_training_version_form_initial_values(self) -> Dict:
        training_version = self.get_program_tree_version_obj()
        form_initial_values = {
            'version_name': training_version.version_name,
            'title': training_version.title_fr,
            'title_english': training_version.title_en,
            'end_year': training_version.end_year_of_existence
        }
        return form_initial_values
