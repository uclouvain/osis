# Register your models here.
from django.contrib import admin

from .auth.roles import faculty_manager
from .models import group, group_year

# Register your models here.
admin.site.register(group.Group,
                    group.GroupAdmin)

admin.site.register(group_year.GroupYear,
                    group_year.GroupYearAdmin)

admin.site.register(
    faculty_manager.FacultyManager,
    faculty_manager.FacultyManagerAdmin,
)
