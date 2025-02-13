import pytest

from activitystream.serializers import ActivityStreamDomesticHCSATUserFeedbackDataSerializer


@pytest.mark.django_db
def test_domestic_hcsat_feedback_serializer(hcsat_instance):

    serializer = ActivityStreamDomesticHCSATUserFeedbackDataSerializer()
    output = serializer.to_representation(hcsat_instance)

    # Remove date due to timezone mismatch

    del output['object']['feedback_submission_date']
    expected = {
        'id': f'dit:domestic:HCSATFeedbackData:{hcsat_instance.id}:Update',
        'type': 'Update',
        'object': {
            'id': hcsat_instance.id,
            'type': 'dit:domestic:HCSATFeedbackData',
            'url': hcsat_instance.url,
            'user_journey': hcsat_instance.user_journey,
            'satisfaction_rating': hcsat_instance.satisfaction_rating,
            'experienced_issues': hcsat_instance.experienced_issues,
            'other_detail': hcsat_instance.other_detail,
            'service_improvements_feedback': hcsat_instance.service_improvements_feedback,
            'likelihood_of_return': hcsat_instance.likelihood_of_return,
            'service_name': hcsat_instance.service_name,
            'service_specific_feedback': hcsat_instance.service_specific_feedback,
            'service_specific_feedback_other': hcsat_instance.service_specific_feedback_other,
        },
    }

    assert output == expected
