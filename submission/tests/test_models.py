import pytest

from client.tests.factories import ClientFactory
from submission import constants, models
from submission.tests import factories


@pytest.fixture
def submission():
    return models.Submission(
        data={'title': 'hello'},
        meta={
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com'],
            'form_url': '/the/form/',
            'funnel_steps': ['one', 'two', 'three'],
            'reply_to': 'test@testsubmission.com',
        },
        client=ClientFactory.build(),
    )


@pytest.mark.django_db
def test_submission_action_name(submission):
    assert submission.action_name == constants.ACTION_NAME_EMAIL


@pytest.mark.django_db
def test_submission_funnel(submission):
    assert submission.funnel == ['one', 'two', 'three']


@pytest.mark.django_db
def test_sender():
    sender = factories.SenderFactory()

    assert str(sender) == sender.email_address


@pytest.mark.django_db
def test_submission_ip_no_sender(submission):
    assert submission.ip_address is None


@pytest.mark.django_db
def test_submission_ip(submission):
    submission.meta['sender'] = {'email_address': 'test@tdfsf.com', 'ip_address': '192.893.21.1'}
    assert submission.ip_address == '192.893.21.1'
