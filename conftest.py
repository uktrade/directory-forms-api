import pytest

from django import db
from django.core.management import call_command
from django.db.migrations.executor import MigrationExecutor

from submission import constants


@pytest.fixture
def email_action_payload():
    return {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com'],
            'subject': 'Hello',
            'reply_to': ['email-user@example.com'],
        }
    }


@pytest.fixture
def zendesk_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_ZENDESK,
            'subject': 'Hello',
            'full_name': 'Jim Example',
            'email_address': 'zendesk-user@example.com',
            'service_name': 'Market Access',
            'form_url': '/some/form/',
            'ingress_url': 'https://www.example.com',
        },
    }


@pytest.fixture
def gov_notify_action_payload_old():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': 'gov-notify',
            'template_id': '213123',
            'email_address': 'notify-user@example.com',
        }
    }


@pytest.fixture
def gov_notify_email_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_GOV_NOTIFY_EMAIL,
            'template_id': '213123',
            'email_address': 'notify-user@example.com',
        }
    }


@pytest.fixture
def gov_notify_letter_action_payload():
    return {
        'data': {
            'address_line_1': 'The Occupier',
            'address_line_2': '123 High Street',
            'postcode': 'SW14 6BF',
            'name': 'John Smith',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_GOV_NOTIFY_LETTER,
            'template_id': '21312345',
        }
    }


@pytest.fixture
def pardot_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_PARDOT,
            'pardot_url': 'http://www.example.com/some/submission/path/',
        }
    }


@pytest.fixture()
def migration(transactional_db):
    """
    This fixture returns a helper object to test Django data migrations.
    The fixture returns an object with two methods;
     - `before` to initialize db to the state before the migration under test
     - `after` to execute the migration and bring db to the state after the
    migration. The methods return `old_apps` and `new_apps` respectively; these
    can be used to initiate the ORM models as in the migrations themselves.
    For example:
        def test_foo_set_to_bar(migration):
            old_apps = migration.before([('my_app', '0001_inital')])
            Foo = old_apps.get_model('my_app', 'foo')
            Foo.objects.create(bar=False)
            assert Foo.objects.count() == 1
            assert Foo.objects.filter(bar=False).count() == Foo.objects.count()
            # executing migration
            new_apps = migration.apply('my_app', '0002_set_foo_bar')
            Foo = new_apps.get_model('my_app', 'foo')
            assert Foo.objects.filter(bar=False).count() == 0
            assert Foo.objects.filter(bar=True).count() == Foo.objects.count()
    From: https://gist.github.com/asfaltboy/b3e6f9b5d95af8ba2cc46f2ba6eae5e2
    """
    class Migrator:
        def before(self, migrate_from):
            """ Specify app and starting migration name as in:
                before(['app', '0001_before']) => app/migrations/0001_before.py
            """

            self.migrate_from = migrate_from
            self.executor = MigrationExecutor(db.connection)
            self.executor.migrate(self.migrate_from)
            self._old_apps = self.executor.loader.project_state(
                self.migrate_from).apps
            return self._old_apps

        def apply(self, app, migrate_to):
            """ Migrate forwards to the "migrate_to" migration """
            self.migrate_to = [(app, migrate_to)]
            self.executor.loader.build_graph()  # reload.
            self.executor.migrate(self.migrate_to)
            self._new_apps = self.executor.loader.project_state(
                self.migrate_to).apps
            return self._new_apps

    yield Migrator()
    call_command('migrate')
