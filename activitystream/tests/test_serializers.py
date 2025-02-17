import pytest

from activitystream.serializers import (
    ActivityStreamDomesticHCSATUserFeedbackDataSerializer,
)


@pytest.mark.django_db
def test_domestic_hcsat_feedback_serializer(hcsat_bulk_instance):

    serializer = ActivityStreamDomesticHCSATUserFeedbackDataSerializer()

    data = hcsat_bulk_instance["hcsat_feedback_entries"][0]
    output = serializer.to_representation(data)

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
