from base.models.group_element_year import GroupElementYear
from program_management.contrib.mixins import PersistentBusinessObject
from program_management.contrib.node import Node


class LinkFactory:
    def get_link(self, group_element_year: GroupElementYear):
        # Can be a relative link / concrete link
        return Link(group_element_year)


factory = LinkFactory()


class Link(PersistentBusinessObject):
    parent: Node = None
    child: Node = None

    map_with_database = {
        GroupElementYear: {
            'link_id': 'id',
            'relative_credits': 'relative_credits',
            'min_credits': 'min_credits',
            'max_credits': 'max_credits',
            #     à compléter ...
        }
    }

    main_queryset_model_class = GroupElementYear

