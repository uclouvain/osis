from education_group.views.mini_training.common_read import MiniTrainingRead, Tab
from program_management.ddd.service import tree_service


class MiniTrainingReadUtilization(MiniTrainingRead):
    template_name = "mini_training/utilization_read.html"
    active_tab = Tab.UTILIZATION

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
