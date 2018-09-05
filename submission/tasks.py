from conf.celery import app

from submission import helpers


@app.task
def create_zendesk_ticket(*args, **kwargs):
    helpers.create_zendesk_ticket(*args, **kwargs)


@app.task
def send_email(*args, **kwargs):
    helpers.send_email(*args, **kwargs)