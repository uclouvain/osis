from django.urls import reverse
from django.views.generic import RedirectView

from program_management.ddd.domain.node import NodeIdentity
from program_management.ddd.repositories.node import NodeRepository

from education_group.views.proxy.read import SUFFIX_CONTENT, SUFFIX_ADMINISTRATIVE_DATA, SUFFIX_DIPLOMAS_CERTIFICATES, \
    SUFFIX_ADMISSION_CONDITION, SUFFIX_SKILLS_ACHIEVEMENTS, SUFFIX_IDENTIFICATION, SUFFIX_UTILIZATION, \
    SUFFIX_GENERAL_INFO


class IdentificationRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        year = self.kwargs['year']
        code = self.kwargs['code']
        root_node = NodeRepository().get(NodeIdentity(code=code, year=year))
        if root_node.is_training():
            url_name_prefix = "training"
            url_kwargs = {'year': root_node.year, 'code': root_node.code}
        elif root_node.is_mini_training():
            url_name_prefix = "mini_training"
            url_kwargs = {'year': root_node.year, 'code': root_node.code}
        elif root_node.is_learning_unit():
            url_name_prefix = "learning_unit"
            url_kwargs = {'year': root_node.year, 'acronym': root_node.code}
        else:
            url_name_prefix = "group"
            url_kwargs = {'year': root_node.year, 'code': root_node.code}
        self.url = reverse(
            "{}_{}".format(url_name_prefix, get_url_name_suffix_from_referer(self.request.META.get('HTTP_REFERER'))),
            kwargs=url_kwargs
        )
        return super().get_redirect_url(*args, **kwargs)


def get_url_name_suffix_from_referer(referer: str):
    url_name_suffixes = [SUFFIX_CONTENT, SUFFIX_ADMINISTRATIVE_DATA, SUFFIX_DIPLOMAS_CERTIFICATES,
                         SUFFIX_ADMISSION_CONDITION, SUFFIX_SKILLS_ACHIEVEMENTS, SUFFIX_IDENTIFICATION,
                         SUFFIX_UTILIZATION, SUFFIX_GENERAL_INFO]
    if referer:
        return next((suffix for suffix in url_name_suffixes if suffix in referer), SUFFIX_IDENTIFICATION)
    return SUFFIX_IDENTIFICATION
