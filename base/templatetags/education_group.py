##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django import template
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe

from base.business.education_groups.perms import is_eligible_to_delete_education_group, \
    is_eligible_to_change_education_group, is_eligible_to_add_education_group

register = template.Library()

# TODO use inclusion tag
li_template = """
<li class="{}">
    <a href="{}" data-toggle="tooltip" id="{}" title="{}">{}</a>
</li>
"""


@register.simple_tag(takes_context=True)
def li_with_deletion_perm(context, url, message, url_id="link_delete"):
    return li_with_permission(context, is_eligible_to_delete_education_group, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_update_perm(context, url, message, url_id="link_update"):
    return li_with_permission(context, is_eligible_to_change_education_group, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_create_perm(context, url, message, url_id="link_create"):
    return li_with_permission(context, is_eligible_to_add_education_group, url, message, url_id)


def li_with_permission(context, permission, url, message, url_id):
    permission_denied_message = ""

    education_group_year = context.get('education_group_year')
    person = context.get('person')
    root = context["request"].GET.get("root", "")

    try:
        result = permission(person, education_group_year, raise_exception=True)

    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    if result:
        li_class = ""
        href = url + "?root=" + root
    else:
        li_class = "disabled"
        href = "#"

    return mark_safe(li_template.format(li_class, href, url_id, permission_denied_message, message))
