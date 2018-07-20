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
import collections

Documentation = collections.namedtuple("Documentation", "name, url, contextual_paths")

GLOBAL = Documentation(
    name="global",
    url="http://uclouvain.github.io/osis/assets/user_manual_fr.pdf",
    contextual_paths=[]
)

EDUCATIONAL_INFORMATION = Documentation(
    name="educational_information",
    url="https://uclouvain-sips.atlassian.net/secure/attachment/11031/2_OSIS_Gestionnaire_Info%20Pedag_15%20juillet%202018.pdf",
    contextual_paths=[]
)

DOCUMENTATIONS = [
    GLOBAL,
    EDUCATIONAL_INFORMATION,
]

def documentation_url(request):
    """
    Context processors that returns list of documentation url.
    The 'global' key corresponds to the url of the general document.
    The 'contextual' key corresponds to the url of the document mapped to the url.
    All other keys corresponds to the topic of the documentation they point to.
    """
    return {
        "documentation_url": {
            doc.name:doc.url for doc in DOCUMENTATIONS
        }
    }