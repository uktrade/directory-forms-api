import pytest
from copy import deepcopy

from submission.constants import BLACKLISTED_REASON_CHOICES


@pytest.mark.django_db
def test_set_gov_notify_email(
    migration, email_action_payload, zendesk_action_payload,
    gov_notify_action_payload_old, pardot_action_payload,
):
    old_apps = migration.before([('submission', '0011_auto_20190110_1403')])
    Submission = old_apps.get_model('submission', 'Submission')

    submission_a = Submission.objects.create(**email_action_payload)
    submission_b = Submission.objects.create(**zendesk_action_payload)
    submission_c = Submission.objects.create(**gov_notify_action_payload_old)
    submission_d = Submission.objects.create(**pardot_action_payload)

    new_apps = migration.apply('submission', '0012_auto_20190705_1706')

    Submission = new_apps.get_model('submission', 'Submission')

    post_submission_a = Submission.objects.get(pk=submission_a.pk)
    post_submission_b = Submission.objects.get(pk=submission_b.pk)
    post_submission_c = Submission.objects.get(pk=submission_c.pk)
    post_submission_d = Submission.objects.get(pk=submission_d.pk)

    assert Submission.objects.count() == 4

    assert post_submission_a.data == email_action_payload['data']
    assert post_submission_a.meta == email_action_payload['meta']

    assert post_submission_b.data == zendesk_action_payload['data']
    assert post_submission_b.meta == zendesk_action_payload['meta']

    gov_notify_action_payload_new = deepcopy(gov_notify_action_payload_old)
    gov_notify_action_payload_new['meta']['action_name'] = 'gov-notify-email'

    assert post_submission_c.data == gov_notify_action_payload_new['data']
    assert post_submission_c.meta == gov_notify_action_payload_new['meta']

    assert post_submission_d.data == pardot_action_payload['data']
    assert post_submission_d.meta == pardot_action_payload['meta']


@pytest.mark.django_db
def test_update_blacklist_reason(migration):
    old_apps = migration.before([('submission', '0013_auto_20191017_1108')])
    Sender = old_apps.get_model('submission', 'Sender')

    sender_1 = Sender.objects.create(email_address='1@example.com', is_blacklisted=True)
    sender_2 = Sender.objects.create(email_address='2@example.com', is_blacklisted=True)
    sender_3 = Sender.objects.create(email_address='3@example.com', is_blacklisted=False)

    new_apps = migration.apply('submission', '0014_auto_20191021_0841')

    Sender = new_apps.get_model('submission', 'Sender')

    post_sender_1 = Sender.objects.get(pk=sender_1.pk)
    post_sender_2 = Sender.objects.get(pk=sender_2.pk)
    post_sender_3 = Sender.objects.get(pk=sender_3.pk)

    assert Sender.objects.count() == 3
    assert post_sender_1.is_blacklisted is True
    assert post_sender_2.is_blacklisted is True
    assert post_sender_3.is_blacklisted is False

    assert post_sender_1.blacklisted_reason == BLACKLISTED_REASON_CHOICES[0][0]
    assert post_sender_2.blacklisted_reason == BLACKLISTED_REASON_CHOICES[0][0]
    assert post_sender_3.blacklisted_reason is None
