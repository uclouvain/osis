##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid
from copy import copy

from django.db.models import QuerySet
from django.forms import model_to_dict


def update_instance_model_from_data(instance, fields_to_update, exclude=()):
    fields_to_update_without_excluded = {field: value for field, value in fields_to_update.items()
                                         if field not in exclude}
    for field, value in fields_to_update_without_excluded.items():
        if hasattr(instance.__class__, field):
            setattr(instance, field, value)
    instance.save()


def update_related_object(obj, attribute_name, new_value, commit_save=True):
    duplicated_obj = duplicate_object(obj)
    setattr(duplicated_obj, attribute_name, new_value)
    if commit_save:
        duplicated_obj.save()
    return duplicated_obj


def duplicate_object(obj):
    new_obj = copy(obj)
    new_obj.pk = None
    new_obj.external_id = None
    new_obj.uuid = uuid.uuid4()
    new_obj.copied_from = obj
    return new_obj


def merge_two_dicts(dict_a, dict_b):
    form_data = dict(dict_a)
    form_data.update(dict_b)
    return form_data


def model_to_dict_fk(instance, exclude=None):
    """
    It allows to transform an instance to a dict.
      - for each FK, it add '_id'
      - All querysetSet will be evaluated in list

    This function is based on model_to_dict implementation.
    """
    data = model_to_dict(instance, exclude=exclude)

    opts = instance._meta
    for fk_field in filter(lambda field: field.is_relation, opts.concrete_fields):
        if fk_field.name in data:
            data[fk_field.name + "_id"] = data.pop(fk_field.name)

    # All the queryset will be evaluate in list.
    for key, value in data.items():
        if isinstance(value, QuerySet):
            data[key] = list(value)

    return data


def compare_objects(dict_1, dict_2):
    return {
        name: (value, dict_2[name])
        for name, value in dict_1.items()
        if dict_1[name] != dict_2[name]
    }


def update_object(obj, new_values_dict):
    """
    set new attr values on an object
    ! list (m2m) attrs will be skipped. This elements should be managed in a M2M update
    """
    for attr, value in new_values_dict.items():
        if not isinstance(value, list):
            setattr(obj, attr, value)
    return obj.save()
