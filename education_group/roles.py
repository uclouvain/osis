from education_group.auth.roles import faculty_manager
from osis_role import role

role.role_manager.register(faculty_manager.FacultyManager)
