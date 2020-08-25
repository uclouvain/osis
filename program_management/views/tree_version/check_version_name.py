import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from osis_common.decorators.ajax import ajax_required
from program_management.models.education_group_version import EducationGroupVersion


@login_required
@ajax_required
@require_http_methods(['GET'])
def check_version_name(request, year, code):
    version_name = request.GET['version_name']
    existed_version_name = False
    old_specific_versions = find_last_existed_version(version_name, year, code)
    existing_version_name = bool(old_specific_versions)
    last_using = None
    if old_specific_versions:
        last_using = str(old_specific_versions.offer.academic_year)
        existed_version_name = True
    valid = bool(re.match("^[A-Z]{0,15}$", request.GET['version_name'].upper()))
    return JsonResponse({
        "existed_version_name": existed_version_name,
        "existing_version_name": existing_version_name,
        "last_using": last_using,
        "valid": valid,
        "version_name": request.GET['version_name']}, safe=False)


def find_last_existed_version(version_name: str, year: int, offer_acronym: str) -> EducationGroupVersion:
    return EducationGroupVersion.objects.filter(
        version_name=version_name.upper(),
        offer__academic_year__year=year,
        offer__acronym=offer_acronym,
        is_transition=False,
    ).order_by(
        'offer__academic_year'
    ).last()
