import pytest
from freezegun import freeze_time

from activitystream.serializers import (
    ActivityStreamDomesticHCSATUserFeedbackDataSerializer,
)
from submission.tests.factories import SubmissionFactory


@pytest.mark.django_db
def test_domestic_hcsat_feedback_serializer(submission_instance):

    serializer = ActivityStreamDomesticHCSATUserFeedbackDataSerializer()

    with freeze_time("2019-09-08 12:00:01"):
        submission = SubmissionFactory(
            form_url="sub_a",
            data=submission_instance["data"],
            meta=submission_instance["meta"],
        )

    output = serializer.to_representation(submission)

    # Remove date due to timezone mismatch

    del output["object"]["feedback_submission_date"]

    expected = {
        "id": "dit:domestic:HCSATFeedbackData:1:Update",
        "type": "Update",
        "object": {
            "id": "dit:domestic:HCSATFeedbackData:1",
            "type": "dit:domestic:HCSATFeedbackData",
            "url": "https://great.gov.uk/export-academy",
            "user_journey": "xxxx",
            "satisfaction_rating": "xxxx",
            "experienced_issues": ["xxxx"],
            "other_detail": "xxxx",
            "service_improvements_feedback": "xxxx",
            "likelihood_of_return": "xxxx",
            "service_name": "export-academy",
            "service_specific_feedback": ["xxxx"],
            "service_specific_feedback_other": "xxxx",
        },
    }

    assert output == expected
