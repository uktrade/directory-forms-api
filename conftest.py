from submission import constants

import pytest


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
            'reply_to': ['reply@example.com'],
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
            'email_address': 'from@example.com',
            'service_name': 'Market Access',
        }
    }


@pytest.fixture
def gov_notify_action_payload():
    return {
        'data': {
            'title': 'hello',
        },
        'meta': {
            'action_name': constants.ACTION_NAME_GOV_NOTIFY,
            'template_id': '213123',
            'email_address': 'from@example.com',
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
