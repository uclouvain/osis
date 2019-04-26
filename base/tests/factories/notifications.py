##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import operator

import factory.fuzzy
import notifications.models
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory
from faker import Faker

from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.user import UserFactory

fake = Faker()


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = "notifications.Notification"
        exclude = ['actor_obj']

    level = factory.Iterator(notifications.models.Notification.LEVELS, getter=operator.itemgetter(0))

    recipient = factory.SubFactory(UserFactory)
    unread = True
    actor_obj = factory.SubFactory(AcademicCalendarFactory)
    actor_content_type = factory.LazyAttribute(lambda notif_obj: ContentType.objects.get_for_model(notif_obj.actor_obj))
    actor_object_id = factory.LazyAttribute(lambda notif_obj: notif_obj.actor_obj.pk)

    verb = "an action"
    description = "a description"
