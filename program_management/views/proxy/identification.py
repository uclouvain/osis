from django.urls import reverse
from django.views.generic import RedirectView

from program_management.ddd.repositories import load_tree


class IdentificationRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        tree = load_tree.load(self.kwargs['root_element_id'])
        self.url = reverse(
            'education_group_read',
            kwargs={'year': tree.root_node.year, 'code': tree.root_node.code}
        )
        return super().get_redirect_url(*args, **kwargs)
