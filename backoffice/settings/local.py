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
from .base import *

OPTIONAL_APPS = (
    'attribution',
    'assistant',
    'continuing_education',
    'dissertation',
    'internship',
    'assessments',
    'cms',
    'webservices',
)
OPTIONAL_MIDDLEWARES = ()
OPTIONAL_INTERNAL_IPS = ()

if os.environ.get("ENABLE_DEBUG_TOOLBAR", "False").lower() == "true":
    OPTIONAL_APPS += ('debug_toolbar',)
    OPTIONAL_MIDDLEWARES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    OPTIONAL_INTERNAL_IPS += ('127.0.0.1',)
    SHOW_TOOLBAR_CALLBACK = 'base.middleware.toolbar.show_toolbar'

INSTALLED_APPS += OPTIONAL_APPS
APPS_TO_TEST += OPTIONAL_APPS
MIDDLEWARE += OPTIONAL_MIDDLEWARES
INTERNAL_IPS += OPTIONAL_INTERNAL_IPS
