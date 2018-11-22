import celery

from conf.celery import app

from submission import helpers, models


class Task(celery.Task):

    def __call__(self, submission_id, *args, **kwargs):
        self.submission_id = submission_id
        return super().__call__(*args, **kwargs)

    def on_success(self, *args, **kwargs):
        submission = models.Submission.objects.get(id=self.submission_id)
        submission.is_sent = True
        submission.save()


@app.task(base=Task)
def create_zendesk_ticket(*args, **kwargs):
    helpers.create_zendesk_ticket(*args, **kwargs)


@app.task(base=Task)
def send_email(*args, **kwargs):
    helpers.send_email(*args, **kwargs)


@app.task(base=Task)
def send_gov_notify(*args, **kwargs):
    helpers.send_gov_notify(*args, **kwargs)


@app.task(base=Task)
def send_pardot(*args, **kwargs):
    helpers.send_pardot(*args, **kwargs)
