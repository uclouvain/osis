from django.conf import settings


def virtual_desktop(request):
    url = ''
    if request.user.person.is_program_manager:
        url = settings.VIRTUAL_DESKTOP_URL
    return {"virtual_desktop_url": url}
