from django.apps import AppConfig


class OsisRoleConfig(AppConfig):
    name = 'osis_role'


class AutodiscoverRoleConfig(OsisRoleConfig):
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('roles')
