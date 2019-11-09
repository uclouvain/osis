from django.http import JsonResponse
from rest_framework.decorators import api_view
from base.models import person as mdl_person


@api_view(['GET'])
def current_user(request):
    user = request.user
    person = mdl_person.find_by_user(user)
    results = {
        'username': user.username,
        'email': person.email,
        'fgs': person.global_id
    }
    resp = JsonResponse(results)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp
