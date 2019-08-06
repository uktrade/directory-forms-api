import pytest
from copy import deepcopy


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
