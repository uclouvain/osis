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
import csv
from time import sleep
from xml.etree import ElementTree

import requests
from django.core.management import BaseCommand

from base.models.education_group_year import EducationGroupYear


class Command(BaseCommand):
    def handle(self, *args, **options):
        template_url = "https://epc.uclouvain.be/WebApi/resources/FicheOffre/code/{acronym}/{academic_year__year}"
        headers = {'Authorization': 'Basic cG9ydGFpbDomRjFuWmVyYg=='}
        scan_list = EducationGroupYear.objects.filter(academic_year__year=2019).values('acronym', 'academic_year__year')[:100]

        path_list = {}
        for idx2, to_scan in enumerate(scan_list):
            response = requests.get(url=template_url.format(**to_scan), headers=headers)
            if response.status_code != 200:
                continue

            tree = ElementTree.fromstring(response.content)
            for idx, data in enumerate(self._get_path_flattened(tree)):
                key = data['path']
                if key in path_list:
                    path_list[key]['count'] += 1
                    # if not idx % 5:
                    #     path_list[key]['example'].extend(data['example'])
                else:
                    path_list[key] = data
            print('Waiting for next... {}'.format(idx2))
            sleep(1)

        with open('offer_fiche_result.csv', mode='w') as csv_file:
            fieldnames = ['path', 'count', 'example']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for result in list(path_list.values()):
                writer.writerow(result)

    def _get_path_flattened(self, root, prefix=''):
        path_list = []
        for child in root:
            to_add = {'path': '.'.join([prefix, child.tag]), 'example': [ElementTree.tostring(child, encoding='utf8')], 'count': 1}
            path_list.append(to_add)
            path_list += self._get_path_flattened(child, prefix=to_add['path'])
        return path_list
