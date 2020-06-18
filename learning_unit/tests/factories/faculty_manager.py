from osis_role.contrib.tests.factories import EntityModelFactory


class FacultyManagerFactory(EntityModelFactory):
    class Meta:
        model = 'learning_unit.FacultyManager'
        django_get_or_create = ('person', 'entity',)
