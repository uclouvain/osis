from django import template

from osis_role import errors

register = template.Library()


@register.inclusion_tag('a_template.html')
def a_tag_has_perm(url, text, perm, user, obj=None):
    context = {"text": text, "url": url}
    has_perm = user.has_perm(perm, obj)
    if not has_perm:
        context.update({
            "url": "#",
            "class_a": "disabled",
            "error_msg": errors.get_permission_errors(user, perm) or ""
        })
    return context


@register.inclusion_tag('a_template.html')
def a_tag_modal_has_perm(url, text, perm, user, obj=None):
    return {
        "class_a": "trigger_modal",
        "load_modal": True,
        **a_tag_has_perm(url, text, perm, user, obj),
    }
