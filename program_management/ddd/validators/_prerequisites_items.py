# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
import re
from typing import List

from django.utils.translation import gettext_lazy as _

from base.ddd.utils.business_validator import BusinessValidator
from program_management.ddd.domain.node import Node
from program_management.ddd.domain.prerequisite import PrerequisiteExpression
from program_management.ddd.validators._prerequisite_expression_syntax import ACRONYM_REGEX


class PrerequisiteItemsValidator(BusinessValidator):
    def __init__(self, prerequisite_string: PrerequisiteExpression, node: Node, codes_permitted: List[str]):
        super().__init__()
        self.prerequisite_string = prerequisite_string
        self.codes_permitted = codes_permitted
        self.node = node

    def validate(self, *args, **kwargs):
        codes_used_in_prerequisite_string = self._extract_acronyms()
        codes_used_but_not_permitted = set(codes_used_in_prerequisite_string) - set(self.codes_permitted)
        if codes_used_but_not_permitted:
            for code in codes_used_but_not_permitted:
                self.add_error_message(
                    _("No match has been found for this learning unit :  %(acronym)s") % {'acronym': code}
                )

        if self.node.code in codes_used_in_prerequisite_string:
            self.add_error_message(
                _("A learning unit cannot be prerequisite to itself : %(acronym)s") % {'acronym': self.node.code}
            )

    def _extract_acronyms(self):
        return re.findall(ACRONYM_REGEX, self.prerequisite_string)
