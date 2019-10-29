from io import StringIO
from core import helpers

import pytest

from submission.tests.factories import SubmissionFactory
from submission.models import Submission


@pytest.mark.django_db
def test_generate_csv():
    SubmissionFactory(data={'html_body': '<html><head></head><body>Hello</body></html>'})
    file_object = StringIO()
    helpers.generate_csv(
        file_object=file_object,
        queryset=Submission.objects.all(),
        excluded_fields=['modified', 'created', 'sender', 'client', 'id', 'form_url', 'is_send']
    )
    file_object.seek(0)

    assert file_object.read() == (
        'data,is_sent,meta\r\nHello,True,"{\'form_url\': \'/the/form/tests\', '
        '\'reply_to\': \'test@testsubmission.com\', \'recipients\': [\'foo@bar.com\'], '
        '\'action_name\': \'email\', \'funnel_steps\': [\'one\', \'two\', \'three\']}"\r\n'
    )
