from datetime import timedelta

import celery
import sentry_sdk
from django.conf import settings
from django.utils import timezone
from requests.exceptions import RequestException

from conf.celery import app
from submission import constants, helpers, models, serializers
from submission.models import Submission


class BaseTask(celery.Task):
    """
    The BaseTask class sets retry / error handling defaults.
    """

    retry_kwargs = {'max_retries': 5}
    exponential_backoff = 2
    retry_jitter = False


class SaveSubmissionTask(BaseTask):
    """
    Used for all legacy V1 API /submission tasks. Ensures submissions are marked as sent when complete.
    """

    def __call__(self, submission_id, *args, **kwargs):
        self.submission_id = submission_id
        return super().__call__(*args, **kwargs)

    def on_success(self, *args, **kwargs):
        submission = models.Submission.objects.get(id=self.submission_id)
        submission.is_sent = True
        submission.save()


@app.task(base=SaveSubmissionTask, autoretry_for=(RequestException,))
def create_zendesk_ticket(*args, **kwargs):
    helpers.create_zendesk_ticket(*args, **kwargs)


@app.task(base=SaveSubmissionTask)
def send_email(*args, **kwargs):
    helpers.send_email(*args, **kwargs)


@app.task(base=SaveSubmissionTask)
def send_gov_notify_email(*args, **kwargs):
    helpers.send_gov_notify_email(*args, **kwargs)


@app.task(base=SaveSubmissionTask)
def send_gov_notify_letter(*args, **kwargs):
    helpers.send_gov_notify_letter(*args, **kwargs)


@app.task(base=SaveSubmissionTask)
def send_pardot(*args, **kwargs):
    helpers.send_pardot(*args, **kwargs)


@app.task(base=SaveSubmissionTask)
def no_operation(*args, **kwargs):
    pass


action_map = {
    constants.ACTION_NAME_EMAIL: (
        send_email,
        serializers.EmailActionSerializer,
    ),
    constants.ACTION_NAME_ZENDESK: (
        create_zendesk_ticket,
        serializers.ZendeskActionSerializer,
    ),
    constants.ACTION_NAME_GOV_NOTIFY_EMAIL: (
        send_gov_notify_email,
        serializers.GovNotifyEmailSerializer,
    ),
    constants.ACTION_NAME_GOV_NOTIFY_LETTER: (
        send_gov_notify_letter,
        serializers.GovNotifyLetterSerializer,
    ),
    constants.ACTION_NAME_PARDOT: (
        send_pardot,
        serializers.PardotSerializer,
    ),
    constants.ACTION_NAME_SAVE_ONLY_IN_DB: (
        no_operation,
        serializers.SaveInDatabaseOnlySerializer,
    ),
}


def execute_for_submission(submission):
    if submission.sender is None or submission.sender.is_enabled:
        task, kwargs_builder_class = action_map[submission.action_name]
        kwargs_builder = kwargs_builder_class.from_submission(submission)
        kwargs_builder.is_valid(raise_exception=True)
        task.delay(
            **kwargs_builder.validated_data,
            submission_id=submission.pk
        )


@app.task()
def send_buy_from_uk_enquiries_as_csv(*args, **kwargs):
    helpers.send_buy_from_uk_enquiries_as_csv(*args, **kwargs)


@app.task(base=BaseTask)
def send_gov_notify_bulk_email():
    """
    Retrieves all submissions for type 'gov-notify-bulk-email' that are not marked as sent, and attempts to
    send an email for them.
    """

    # Get submissions to process - filter any that are older than the SUBMISSION_FILTER_HOURS setting.
    time_delay = timezone.now() - timedelta(hours=settings.SUBMISSION_FILTER_HOURS)
    submissions = Submission.objects.filter(is_sent=False, created__gte=time_delay)

    # We have to do a secondary filter here as Django ORM does not support filtering on @property methods.
    submissions = [x for x in submissions if x.action_name == constants.ACTION_NAME_GOV_NOTIFY_BULK_EMAIL]

    for submission in submissions:
        try:
            helpers.send_gov_notify_email(
                template_id=submission.meta['template_id'],
                email_address=submission.recipient_email,
                personalisation=submission.data
            )
            # Mark email as sent
            submission.is_sent = True
            submission.save()

        except Exception as e:
            sentry_sdk.capture_message(
                f'Sending gov.notify bulk email notification failed for {submission.id}: {e}', 'fatal'
            )
