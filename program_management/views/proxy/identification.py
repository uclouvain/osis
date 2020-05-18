from django.urls import reverse
from django.views.generic import RedirectView

from base.models.enums.education_group_types import GroupType, TrainingType, MiniTrainingType
from program_management.ddd.repositories import load_tree


class IdentificationRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        tree = load_tree.load(self.kwargs['root_element_id'])
        if tree.root_node.category.name in GroupType.get_names():
            url_name = "group_identification"
            url_kwargs = {'year': tree.root_node.year, 'code': tree.root_node.code}
        elif tree.root_node.category.name in TrainingType.get_names():
            url_name = "training_identification"
            url_kwargs = {'year': tree.root_node.year, 'code': tree.root_node.code}
        elif tree.root_node.category.name in MiniTrainingType.get_names():
            url_name = "mini_training_identification"
            url_kwargs = {'year': tree.root_node.year, 'code': tree.root_node.code}
        else:
            url_name = "learning_unit"
            url_kwargs = {'year': tree.root_node.year, 'acronym': tree.root_node.code}
        self.url = reverse(url_name, kwargs=url_kwargs)
        return super().get_redirect_url(*args, **kwargs)
