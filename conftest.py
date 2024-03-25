import pytest

from django import db
from django.core.management import call_command
from django.db.migrations.executor import MigrationExecutor
from unittest import mock

from submission import constants


@pytest.fixture
def erp_zendesk_payload():
    return {
        'meta': {
                'action_name': constants.ACTION_NAME_ZENDESK,
                'email_address': 'erp+testform+testform@gmail.com',
                'full_name': 'test test',
                'funnel_steps': [],
                'ingress_url': 'https://erp.service.dev.uktrade.io/triage/',
                'sender': {'country_code': None,
                           'email_address': 'erp+testform@jhgk.com'},
                'service_name': 'erp',
                'spam_control': {},
                'subject': 'ERP form was submitted'
        },
        'data': {
                'commodities': '190300 - Other',
                'company_name': 'TASTE OF FOOD',
                'company_number': '2387892',
                'company_type': 'LIMITED',
                'email': 'erp+testform@gmail.com',
                'employees': '1-10',
                'employment_regions': ['NORTH_EAST'],
                'family_name': 'test',
                'given_name': 'test',
                'has_market_price_changed': False,
                'has_market_size_changed': False,
                'has_other_changes': False,
                'has_price_changed': False,
                'has_volume_changed': False,
                'market_size_known': False,
                'other_information': 'test',
                'quarter_four_2018': '0',
                'quarter_one_2019': '0',
                'quarter_three_2019': '0',
                'quarter_two_2019': '0',
                'sales_volume_unit': 'KILOGRAM',
                'sector': 'AEROSPACE',
                'tariff_quota': 'N/A',
                'tariff_rate': 'N/A',
                'turnover': '0-25k'
            },
    }


@pytest.fixture
def email_action_payload():
    return {
        'data': {
            'text_body': 'hello there',
            'html_body': '<a>Hello there</a>',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com', 'foo2@bar.com'],
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
            'sort_fields_alphabetically': True
        },
    }


# This payload is to support backward compatibility with gov-notify action
# which is replaced by gov-notify-email eventually this can be removed.
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
            'sender': {
                'country_code': None,
                'email_address': 'erp+testform@jhgk.com',
                'ip_address': '252.252.928.233'
            },
        }
    }


@pytest.fixture
def gov_notify_bulk_email_action_payload():
    return {
            'template_id': '1234',
            'bulk_email_entries': [
                {'name': 'one', 'email_address': 'one@example.com'},
                {'name': 'two', 'email_address': 'two@example.com'},
                {'name': 'three', 'email_address': 'three@example.com'}
            ],
            'email_reply_to_id': '5678',
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


@pytest.fixture(autouse=False)
def mock_middleware_test_sig():
    yield mock.patch(
        'client.helpers.RequestSignatureChecker.test_signature',
        return_value=True,
    ).start()
