from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(['POST'])
def publish_common_admission(request):
    pass


@login_required
@require_http_methods(['POST'])
def publish_common_pedagogy(request):
    pass
