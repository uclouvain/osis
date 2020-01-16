from abc import ABC
from typing import List, Dict, Set

from django.db.models import Model, QuerySet


ModelFieldName = str
BusinessFieldName = str


class BusinessObject(ABC):

    # Permet de savoir à partir de quels modèles est composé l'objet business
    # Permet de connaître les attributs de l'objet business
    # Permet de lier les attributs de l'objet business aux attributs en DB
    map_with_database: Dict[Model, Dict[BusinessFieldName, ModelFieldName]] = None

    _map_all_fields: Dict[BusinessFieldName, ModelFieldName] = None

    def __init__(self):
        assert self.map_with_database is not None
        self._raise_if_duplicate_field_name()

    @property
    def business_field_names(self):
        return self.map_all_field_names.keys()

    @property
    def primary_key_field_names(self) -> Set[BusinessFieldName]:
        return set(
            ModelClass.objects.model._meta.db_table + "id"
            for ModelClass in self.map_with_database.keys()
        )

    @property
    def map_all_field_names(self) -> Dict[BusinessFieldName, ModelFieldName]:
        if not self._map_all_fields:
            self._map_all_fields = {
                business_field_name
                for map_attrs in self.map_with_database.values()
                for business_field_name, model_field_name in map_attrs.items()
            }
        return self._map_all_fields

    @property
    def map_field_name_with_model_class(self) -> Dict[BusinessFieldName: Model]:
        if not self._map_field_name_with_model_class:
            self._map_field_name_with_model_class = {
                business_field_name: model_class
                for model_class, map_attrs in self.map_with_database.items()
                for business_field_name in map_attrs.keys()
            }
        return self._map_field_name_with_model_class

    def _raise_if_duplicate_field_name(self):
        all_attrs = set()
        for map_attrs in self.map_with_database.values():
            for business_field_name in map_attrs.keys():
                if business_field_name in all_attrs:
                    raise AttributeError("Duplicate field in your Business Object : {}".format(business_field_name))
                all_attrs.add(business_field_name)


class FetchedBusinessObject(BusinessObject):

    # Permet d'identifier l'identifiant unique de l'objet business
    # Cette clé étant mappée avec une PK d'une table en DB ("master object")
    main_queryset_model_class: Model = None

    pk_value: int = None

    _object = None

    def __init__(self, pk=None):
        super(FetchedBusinessObject, self).__init__()
        assert self.main_queryset_model_class is not None
        self.pk_value = pk
        self._raise_if_missing_pk()
        self._set_attrs(pk)

    def _raise_if_missing_pk(self):
        for primary_key_field_name in self.primary_key_field_names:
            if primary_key_field_name not in self.business_field_names:
                raise AttributeError("Missing mapping for the primary key : {}".format(primary_key_field_name))

    def get_object(self):
        if not self._object:
            self._object = self.fetch().get(pk=self.pk_value)
        return self._object

    def _set_attrs(self):
        obj = self.get_object()
        self._raise_if_pk_is_not_set(obj)
        for business_field_name in self.business_field_names:
            value = getattr(obj, business_field_name, None)
            setattr(self, business_field_name, value)

    def fetch(self) -> QuerySet:
        return self.main_queryset_model_class.objects.none()

    def _raise_if_pk_is_not_set(self, obj):
        for primary_key_field_name in self.primary_key_field_names:
            if not hasattr(obj, primary_key_field_name):
                raise AttributeError("Missing field {} into your queryset".format(primary_key_field_name))


class PersistentBusinessObject(BusinessObject):

    fields_to_persist: List[ModelFieldName] = None

    def __init__(self, initial_values=None):
        super(PersistentBusinessObject, self).__init__()
        self._set_initial_values(initial_values)

    def _set_initial_values(self, initial_values):
        if initial_values:
            self._raise_if_field_to_set_does_not_exist(initial_values)
            self._raise_if_missing_fields_to_set(initial_values)
            for key, value in initial_values:
                setattr(self, key, value)

    def _raise_if_field_to_set_does_not_exist(self, initial_values):
        inexisting_fields = set(initial_values.keys()) - self.business_field_names
        if inexisting_fields:
            error_msg = "You're trying to set the field '{}' that not exists in this object. " \
                        "Existing fields are : {}".format(inexisting_fields, self.business_field_names)
            raise AttributeError("%s" % error_msg)

    def _raise_if_missing_fields_to_set(self, initial_values):
        missing_fields = self.business_field_names - set(initial_values.keys())
        if missing_fields:
            error_msg = "The following fields are missing in your initial_data : {} ".format(missing_fields)
            raise AttributeError("%s" % error_msg)

    def save(self):
        for ModelClass, map_attrs in self.map_with_database.items():
            instance_values = {
                model_field_name: getattr(self, business_field_name, None)
                for business_field_name, model_field_name in map_attrs.items()
            }
            ModelClass(**instance_values).save()
