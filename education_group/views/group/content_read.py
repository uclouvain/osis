from education_group.views.group.common_read import Tab, GroupRead


class GroupReadContent(GroupRead):
    template_name = "group/content_read.html"
    active_tab = Tab.CONTENT

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "children": self.get_object().children
        }
