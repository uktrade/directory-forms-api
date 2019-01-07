import pytest

from client.tests.factories import ClientFactory
from submission import constants, models


@pytest.fixture
def submission():
    return models.Submission(
        data={'title': 'hello'},
        meta={
            'action_name': constants.ACTION_NAME_EMAIL,
            'recipients': ['foo@bar.com'],
            'form_url': '/the/form/',
            'funnel_steps': ['one', 'two', 'three'],
        },
        client=ClientFactory.build(),
    )


@pytest.mark.django_db
def test_action_name(submission):
    assert submission.action_name == constants.ACTION_NAME_EMAIL


@pytest.mark.django_db
def test_funnel(submission):
    assert submission.funnel == ['one', 'two', 'three']
