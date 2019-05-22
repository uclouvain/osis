# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import collections
import sys

from behave.__main__ import main as behave_main
from behave_django.environment import monkey_patch_behave, BehaveHooksMixin
from behave_django.management.commands.behave import Command as Cmd
from behave_django.testcase import ExistingDatabaseTestCase
from django.conf import settings
from django.db import connection, connections, DEFAULT_DB_ALIAS
from django.test.runner import DiscoverRunner
from django.test.utils import dependency_ordered


def get_unique_databases_and_mirrors():
    """
    Figure out which databases actually need to be created.

    Deduplicate entries in DATABASES that correspond the same database or are
    configured as test mirrors.

    Return two values:
    - test_databases: ordered mapping of signatures to (name, list of aliases)
                      where all aliases share the same underlying database.
    - mirrored_aliases: mapping of mirror aliases to original aliases.
    """
    mirrored_aliases = {}
    test_databases = {}
    dependencies = {}

    settings_dict = connections[DEFAULT_DB_ALIAS].creation.connection.settings_dict
    default_sig = (
        settings_dict['HOST'],
        settings_dict['PORT'],
        settings_dict['ENGINE'],
        settings_dict['NAME'],
    )

    for alias in connections:
        connection = connections[alias]
        test_settings = connection.settings_dict['TEST']

        if test_settings['MIRROR']:
            # If the database is marked as a test mirror, save the alias.
            mirrored_aliases[alias] = test_settings['MIRROR']
        else:
            # Store a tuple with DB parameters that uniquely identify it.
            # If we have two aliases with the same values for that tuple,
            # we only need to create the test database once.
            item = test_databases.setdefault(
                connection.creation.test_db_signature(),
                (connection.settings_dict['NAME'], set())
            )
            item[1].add(alias)

            if 'DEPENDENCIES' in test_settings:
                dependencies[alias] = test_settings['DEPENDENCIES']
            else:
                if alias != DEFAULT_DB_ALIAS and connection.creation.test_db_signature() != default_sig:
                    dependencies[alias] = test_settings.get('DEPENDENCIES', [DEFAULT_DB_ALIAS])

    test_databases = dependency_ordered(test_databases.items(), dependencies)
    test_databases = collections.OrderedDict(test_databases)
    return test_databases, mirrored_aliases


def setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, **kwargs):
    """
    Create the test databases.
    """
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors()

    old_names = []

    for signature, (db_name, aliases) in test_databases.items():
        first_alias = None
        # Backup the current db.
        # backup_name = db_name + '_backup'
        # send_sql("DROP DATABASE IF EXISTS {}".format(backup_name))
        # send_sql("CREATE DATABASE {} WITH TEMPLATE {}".format(backup_name, db_name))
        for alias in aliases:
            connection = connections[alias]
            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                test_db_name = connection.creation._get_test_db_name()
                send_sql("DROP DATABASE IF EXISTS {}".format(test_db_name))
                send_sql("CREATE DATABASE {} WITH TEMPLATE {}".format(test_db_name, db_name))
                connection.creation.connection.close()
                settings.DATABASES[connection.creation.connection.alias]["NAME"] = test_db_name
                connection.creation.connection.settings_dict["NAME"] = test_db_name
                if parallel > 1:
                    for index in range(parallel):
                        connection.creation.clone_test_db(
                            number=index + 1,
                            verbosity=verbosity,
                            keepdb=keepdb,
                        )
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(
            connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names


class CloneExistingDatabaseTestRunner(DiscoverRunner, BehaveHooksMixin):
    """
    Test runner that uses the ExistingDatabaseTestCase

    This test runner nullifies Django's test database setup methods. Using this
    test runner would make your tests run with the default configured database
    in settings.py.
    """
    testcase_class = ExistingDatabaseTestCase

    def setup_databases(self, **kwargs):
        return setup_databases(
            self.verbosity, self.interactive, self.keepdb, self.debug_sql,
            self.parallel, **kwargs
        )

    def teardown_databases(self, old_config, **kwargs):
        """
        Destroys all the non-mirror databases.
        """
        pass


def send_sql(cmd: str):
    with connection.cursor() as cursor:
        cursor.execute(cmd, )


class Command(Cmd):
    def handle(self, *args, **options):
        django_test_runner = CloneExistingDatabaseTestRunner()
        django_test_runner.setup_test_environment()
        old_config = django_test_runner.setup_databases()

        # Run Behave tests
        monkey_patch_behave(django_test_runner)
        behave_args = self.get_behave_args()
        exit_status = behave_main(args=behave_args)

        # Teardown django environment
        django_test_runner.teardown_databases(old_config)
        django_test_runner.teardown_test_environment()

        if exit_status != 0:
            sys.exit(exit_status)
