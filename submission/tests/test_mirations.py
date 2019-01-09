import pytest


@pytest.mark.django_db
def test_set_sender(
    migration, email_action_payload, zendesk_action_payload,
    gov_notify_action_payload, pardot_action_payload
):
    old_apps = migration.before([('submission', '0009_auto_20190109_0904')])
    Submission = old_apps.get_model('submission', 'Submission')

    submission_a = Submission.objects.create(**email_action_payload)
    submission_b = Submission.objects.create(**zendesk_action_payload)
    submission_c = Submission.objects.create(**gov_notify_action_payload)
    submission_d = Submission.objects.create(**pardot_action_payload)

    new_apps = migration.apply('submission', '0010_auto_20190109_0915')

    Submission = new_apps.get_model('submission', 'Submission')
    Sender = new_apps.get_model('submission', 'Sender')

    assert Sender.objects.count() == 3

    sender_a = Sender.objects.get(
        email_address=email_action_payload['meta']['reply_to'][0]
    )
    sender_b = Sender.objects.get(
        email_address=zendesk_action_payload['meta']['email_address']
    )
    sender_c = Sender.objects.get(
        email_address=gov_notify_action_payload['meta']['email_address']
    )

    assert Submission.objects.get(pk=submission_a.pk).sender == sender_a
    assert Submission.objects.get(pk=submission_b.pk).sender == sender_b
    assert Submission.objects.get(pk=submission_c.pk).sender == sender_c
    assert Submission.objects.get(pk=submission_d.pk).sender is None
