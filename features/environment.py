# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def before_all(context):
    options = Options()
    if settings.SELENIUM_SETTINGS["VIRTUAL_DISPLAY"]:
        options.add_argument('-headless')
    executable_path = settings.SELENIUM_SETTINGS["GECKO_DRIVER"]
    context.browser = webdriver.Firefox(options=options, executable_path=executable_path)


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    pass


def after_all(context):
    context.browser.quit()

def after_step(context, step):
    if settings.SELENIUM_SETTINGS["TAKE_SCREEN_ON_FAILURE"] and step.status == "failed":
        context.browser.save_screenshot("features/logs/failure_{}{}.png".format(context.feature.name, step.name))
