from osis_role.contrib.tests.factories import EntityModelFactory


class FacultyManagerFactory(EntityModelFactory):
    class Meta:
        model = 'education_group.FacultyManager'

    scopes = ['ALL']
