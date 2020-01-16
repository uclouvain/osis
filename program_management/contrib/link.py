from base.models.group_element_year import GroupElementYear
from program_management.contrib.mixins import PersistentBusinessObject


class Link(PersistentBusinessObject):
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

