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
from operator import itemgetter

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from base.models.campus import Campus
from base.models.entity import Entity
from base.models.organization import Organization
from base.models.organization_address import find_distinct_by_country
from osis_common.decorators.ajax import ajax_required


# TODO :: On peut combiner les différentes vues en faisant passer les paramètres via le GET et en uniformisant
# le JsonResponse.
@ajax_required
def filter_cities_by_country(request):
    """ Ajax request to filter the cities choice field """
    country = request.GET.get('country')
    cities = find_distinct_by_country(country)
    return JsonResponse(list(cities), safe=False)


@ajax_required
def filter_campus_by_city(request):
    """ Ajax request to filter the campus choice field """
    city = request.GET.get('city')
    campuses = Campus.objects.filter(
        organization__organizationaddress__city=city
    ).distinct('organization__name').order_by('organization__name').values('pk', 'organization__name')
    return JsonResponse(list(campuses), safe=False)
