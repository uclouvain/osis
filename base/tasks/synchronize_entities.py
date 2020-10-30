import datetime

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from backoffice.celery import app as celery_app
from base.models.entity import Entity
from base.models.entity_version import EntityVersion
from base.models.enums import organization_type, entity_type
from base.models.organization import Organization

# DOCKER: sudo docker run --net=host --rm -e RABBITMQ_DEFAULT_USER=guest -e RABBITMQ_DEFAULT_PASS=guest rabbitmq
# CELERY: celery -A backoffice worker -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


@celery_app.task
def run():
    raw_entities = _fetch_entities_from_esb()

    raw_root_entity = next(entity for entity in raw_entities if entity['parent_entity_id'] == {"@nil": "true"})
    _upsert_entity(raw_root_entity)
    _save_children_entities(raw_root_entity, raw_entities)


def _fetch_entities_from_esb():
    if not all([settings.ESB_API_URL, settings.ESB_ENTITIES_HISTORY_ENDPOINT]):
        raise ImproperlyConfigured('ESB_API_URL / ESB_ENTITIES_HISTORY_ENDPOINT must be set in configuration')

    endpoint = settings.ESB_ENTITIES_HISTORY_ENDPOINT
    url = "{esb_api}/{endpoint}".format(esb_api=settings.ESB_API_URL, endpoint=endpoint)
    try:
        entities_wrapped = requests.get(
            url,
            headers={"Authorization": settings.ESB_AUTHORIZATION},
            timeout=settings.REQUESTS_TIMEOUT or 20
        )
        return entities_wrapped.json()['entities']
    except Exception:
        raise FetchEntitiesException


def _save_children_entities(raw_entity, all_raw_entities):
    for child_entity in filter(lambda entity: entity['parent_entity_id'] == raw_entity, all_raw_entities):
        _upsert_entity(child_entity)
        _save_children_entities(child_entity, all_raw_entities)


def _upsert_entity(raw_entity):
    entity = Entity.objects.update_or_create(
        external_id='osis.entity_{}'.format(raw_entity['entity_id']),
        defaults={
            'website': raw_entity['web'] or '',
            'organization_id': Organization.objects.only('pk').get(type=organization_type.MAIN)
        }
    )

    EntityVersion.objects.get_or_create(
        entity=entity,
        acronym=raw_entity['acronym'],
        parent_id=Entity.objects.only('pk').get(external_id='osis.entity_{}'.format(raw_entity['parent_entity_id'])),
        title=raw_entity['name_fr'],
        entity_type=__get_entity_type(raw_entity),
        start_date=ESBDate(raw_entity['begin']).to_date(),
        end_date=ESBDate(raw_entity['end']).to_date(),
    )


def __get_entity_type(raw_entity):
    return {
        'S': entity_type.SECTOR,
        'F': entity_type.FACULTY,
        'E': entity_type.SCHOOL,
        'I': entity_type.INSTITUTE,
        'P': entity_type.POLE,
        'D': entity_type.DOCTORAL_COMMISSION,
        'T': entity_type.PLATFORM,
        'L': entity_type.LOGISTICS_ENTITY,
        'N': None,
    }.get(raw_entity['departmentType'])


class ESBDate(int):
    """
    The date format comming from ESB data is in format 20100101 which means 01/01/2010
    The undefined value is represented as 99991231
    """
    def to_date(self):
        if self == 99991231:
            return None
        date_str = str(self)
        return datetime.date(year=int(date_str[0:4]), month=int(date_str[4:6]), day=int(date_str[6:8]))


class FetchEntitiesException(Exception):
    def __init__(self, **kwargs):
        self.message = "Unable to fetch entities data"
        super().__init__(**kwargs)
