import celery
from requests.exceptions import RequestException

from conf.celery import app
from submission import constants, helpers, models, serializers


class Task(celery.Task):

    retry_kwargs = {'max_retries': 5}
    exponential_backoff = 2
    retry_jitter = False

    def __call__(self, submission_id, *args, **kwargs):
        self.submission_id = submission_id
        return super().__call__(*args, **kwargs)

    def on_success(self, *args, **kwargs):
        submission = models.Submission.objects.get(id=self.submission_id)
        submission.is_sent = True
        submission.save()


@app.task(base=Task, autoretry_for=(RequestException,))
def create_zendesk_ticket(*args, **kwargs):
    helpers.create_zendesk_ticket(*args, **kwargs)


@app.task(base=Task)
def send_email(*args, **kwargs):
    helpers.send_email(*args, **kwargs)


@app.task(base=Task)
def send_gov_notify_email(*args, **kwargs):
    helpers.send_gov_notify_email(*args, **kwargs)


@app.task(base=Task)
def send_gov_notify_letter(*args, **kwargs):
    helpers.send_gov_notify_letter(*args, **kwargs)


@app.task(base=Task)
def send_pardot(*args, **kwargs):
    helpers.send_pardot(*args, **kwargs)


@app.task(base=Task)
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
