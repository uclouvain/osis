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
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from base.business.education_groups.perms import is_eligible_to_delete_education_group, \
    is_eligible_to_change_education_group, is_eligible_to_add_education_group

register = template.Library()

# TODO use inclusion tag
LI_TEMPLATE = """
<li class="{}" id="{}">
    <a href="{}" data-toggle="tooltip" title="{}">{}</a>
</li>
"""

BUTTON_TEMPLATE = """
<button title="{}" class="btn btn-default btn-sm" id="{}" data-toggle="tooltip-wrapper" name="action" {}>
    <i class="fa {}"></i>
</button>
"""

BUTTON_ORDER_TEMPLATE = """
<button type="submit" title="{}" class="btn btn-default btn-sm" 
    id="{}" data-toggle="tooltip-wrapper" name="action" value="{}" {}>
    <i class="fa {}"></i>
</button>
"""

ICONS = {
    "up": "fa-arrow-up",
    "down": "fa-arrow-down",
    "detach": "fa-close",
    "edit": "fa-edit",
}


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
    permission_denied_message, disabled, root = _get_permission(context, permission)

    if not disabled:
        href = url + "?root=" + root
    else:
        href = "#"

    return mark_safe(LI_TEMPLATE.format(disabled, url_id, href, permission_denied_message, message))


def _get_permission(context, permission):
    permission_denied_message = ""

    education_group_year = context.get('education_group_year')
    person = context.get('person')
    root = context["request"].GET.get("root", "")

    try:
        result = permission(person, education_group_year, raise_exception=True)

    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    return permission_denied_message, "" if result else "disabled", root


@register.simple_tag(takes_context=True)
def button_order_with_permission(context, title, id_button, value):
    permission_denied_message, disabled, root = _get_permission(context, is_eligible_to_change_education_group)

    if disabled:
        title = permission_denied_message

    if value == "up" and context["forloop"]["first"]:
        disabled = "disabled"

    if value == "down" and context["forloop"]["last"]:
        disabled = "disabled"

    return mark_safe(BUTTON_ORDER_TEMPLATE.format(title, id_button, value, disabled, ICONS[value]))


@register.simple_tag(takes_context=True)
def button_with_permission(context, title, id_a, value):
    permission_denied_message, disabled, root = _get_permission(context, is_eligible_to_change_education_group)

    if disabled:
        title = permission_denied_message

    return mark_safe(BUTTON_TEMPLATE.format(title, id_a, disabled, ICONS[value]))


@register.filter(is_safe=True, needs_autoescape=True)
def tree_list(value, autoescape=True):
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x):
            return x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if not isinstance(next_item, six.string_types):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = '\t' * tabs
        output = []
        for item, children in walk_items(item_list):
            sublist = ''
            case = ''
            if children:
                sublist = '\n%s<ul>\n%s\n%s</ul>\n%s' % (
                    indent, list_formatter(children, tabs + 1), indent, indent)

            if item.child_leaf:
                if item.is_mandatory:
                    output.append('%s<li style="list-style-type: none;">[ ][O]%s%s</li>' % (
                        indent, escaper(force_text(item.verbose)), sublist))
                else:
                    output.append('%s<li style="list-style-type: none;">[ ][F]%s%s</li>' % (
                        indent, escaper(force_text(item.verbose)), sublist))
            else:
                if item.is_mandatory:
                    output.append('%s<li style="list-style-type: none;">[O]%s%s</li>' % (
                        indent, escaper(force_text(item.verbose)), sublist))
                else:
                    output.append('%s<li style="list-style-type: none;">[F]%s%s</li>' % (
                        indent, escaper(force_text(item.verbose)), sublist))
        return '\n'.join(output)

    return mark_safe(list_formatter(value))
