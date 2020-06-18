from osis_role.contrib.tests.factories import EntityModelFactory


class CentralManagerFactory(EntityModelFactory):
    class Meta:
        model = 'learning_unit.CentralManager'
        django_get_or_create = ('person', 'entity',)
