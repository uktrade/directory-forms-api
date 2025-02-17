import datetime

import mohawk
import pytest
from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from activitystream.serializers import SubmissionSerializer
from submission.models import Submission
from submission.tests.factories import SubmissionFactory

URL = "http://testserver" + reverse("activity-stream")
URL2 = "http://testserver" + reverse("activity-stream-hcsat")
URL_INCORRECT_DOMAIN = "http://incorrect" + reverse("activity-stream")
URL_INCORRECT_PATH = "http://testserver" + reverse("activity-stream") + "incorrect/"

EMPTY_COLLECTION = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Collection",
    "orderedItems": [],
}


@pytest.fixture
def api_client():
    return APIClient()


def submission_attribute(activity, attribute):
    return activity["object"][attribute]


def auth_sender(
    key_id=settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
    secret_key=settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
    url=URL,
    method="GET",
    content="",
    content_type="",
):
    credentials = {
        "id": key_id,
        "key": secret_key,
        "algorithm": "sha256",
    }

    return mohawk.Sender(
        credentials,
        url,
        method,
        content=content,
        content_type=content_type,
    )


# --- Authentication tests ---


@pytest.mark.django_db
def test_empty_object_returned_with_authentication(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    sender = auth_sender()

    response = api_client.get(
        URL,
        content_type="",
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == EMPTY_COLLECTION

    # sender.accept_response will raise an error if the
    # inputs are not valid
    sender.accept_response(
        response_header=response["Server-Authorization"],
        content=response.content,
        content_type=response["Content-Type"],
    )
    with pytest.raises(mohawk.exc.MacMismatch):
        sender.accept_response(
            response_header=response["Server-Authorization"] + "incorrect",
            content=response.content,
            content_type=response["Content-Type"],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response["Server-Authorization"],
            content="incorrect",
            content_type=response["Content-Type"],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response["Server-Authorization"],
            content=response.content,
            content_type="incorrect",
        )


@pytest.mark.django_db
def test_authentication_fails_if_url_mismatched(api_client):
    """Creates a Hawk header with incorrect domain"""
    sender = auth_sender(url=URL_INCORRECT_DOMAIN)
    response = api_client.get(
        URL,
        content_type="",
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    """Creates a Hawk header with incorrect path"""
    sender = auth_sender(url=URL_INCORRECT_PATH)
    response = api_client.get(
        URL,
        content_type="",
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = timezone.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = auth_sender().request_header
    response = api_client.get(
        reverse("activity-stream"),
        content_type="",
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {"detail": "Incorrect authentication credentials."}
    assert response.json() == error


# --- Content tests ---


@pytest.mark.django_db
def test_lists_sent_submissions_in_stream(
    api_client, erp_zendesk_payload, email_action_payload
):
    # Create the articles

    with freeze_time("2019-09-08 12:00:01"):
        SubmissionFactory(
            form_url="sub_a",
            data=erp_zendesk_payload["data"],
            meta=erp_zendesk_payload["meta"],
        )

    with freeze_time("2019-09-08 12:00:02"):
        SubmissionFactory(
            form_url="sub_b",
            data=erp_zendesk_payload["data"],
            meta=erp_zendesk_payload["meta"],
        )

    with freeze_time("2019-09-08 12:00:03"):
        SubmissionFactory(
            form_url="sub_c",
            data=email_action_payload["data"],
            meta=email_action_payload["meta"],
        )

    sender = auth_sender()

    response = api_client.get(
        URL,
        content_type="",
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    items = response.json()["orderedItems"]

    id_prefix = "dit:directoryFormsApi:Submission:"
    id_prefix_sender = "dit:directoryFormsApi:Sender:"

    i = 0
    for submission in Submission.objects.all().order_by("id"):
        serializer = SubmissionSerializer(submission)
        assert submission_attribute(items[i], "id") == id_prefix + str(submission.id)
        assert items[i]["actor"] == serializer.data["actor"]
        assert items[i]["actor"]["id"] == id_prefix_sender + str(submission.sender.id)
        assert items[i]["object"] == serializer.data["object"]
        assert (
            submission_attribute(items[i], "dit:directoryFormsApi:Submission:Meta")
            == submission.meta
        )
        assert (
            submission_attribute(items[i], "dit:directoryFormsApi:Submission:Data")
            == submission.data
        )
        assert submission_attribute(items[i], "attributedTo")["type"] == (
            "dit:directoryFormsApi:SubmissionAction:" + submission.action_name
        )
        assert submission_attribute(items[i], "attributedTo")["id"] == (
            "dit:directoryFormsApi:SubmissionType:"
            + submission.client.name.replace(" ", "")
        )
        i += 1

    assert items[0]["published"] == "2019-09-08T12:00:01+00:00"
    assert items[1]["published"] == "2019-09-08T12:00:02+00:00"
    assert items[2]["published"] == "2019-09-08T12:00:03+00:00"


@pytest.mark.django_db
def test_pagination(
    api_client, django_assert_num_queries, erp_zendesk_payload, email_action_payload
):
    """The requests are paginated, ending on a submission without a next key"""

    """ create 50 submission. Second set should appear in feed first. """
    with freeze_time("2012-01-14 12:00:02"):
        for i in range(0, 25):
            SubmissionFactory(
                form_url="submission_{}".format(i),
                data=erp_zendesk_payload["data"],
                meta=erp_zendesk_payload["meta"],
            )

    with freeze_time("2012-01-14 12:00:01"):
        for i in range(25, 50):
            SubmissionFactory(
                form_url="submission_{}".format(i),
                data=email_action_payload["data"],
                meta=email_action_payload["meta"],
            )

    items = []
    next_url = URL
    num_pages = 0

    """ One query to pull items 0 -> 24,
        Two queries to pull items 25 -> 49 due to filter being used,
        No queries on final blank page
    """

    with django_assert_num_queries(103):
        while next_url:
            num_pages += 1
            sender = auth_sender(url=next_url)
            response = api_client.get(
                next_url,
                content_type="",
                HTTP_AUTHORIZATION=sender.request_header,
                HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
            )
            response_json = response.json()
            items += response_json["orderedItems"]
            next_url = response_json["next"] if "next" in response_json else None

    assert num_pages == 3
    assert len(items) == 50
    assert len(set([item["id"] for item in items])) == 50  # All unique
    assert submission_attribute(items[49], "url") == "submission_24"


@pytest.mark.django_db
def test_hcsat_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = timezone.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = auth_sender().request_header
    response = api_client.get(
        reverse("activity-stream-hcsat"),
        content_type="",
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {"detail": "Incorrect authentication credentials."}
    assert response.json() == error


@pytest.mark.django_db
def test_hcsat_success(api_client, submission_instance):

    with freeze_time("2012-01-14 12:00:01"):
        for i in range(0, 2):
            SubmissionFactory(
                form_url="submission_{}".format(i),
                data=submission_instance["data"],
                meta=submission_instance["meta"],
            )

        sender = auth_sender(url=URL2)

        response = api_client.get(
            URL2,
            content_type="",
            HTTP_AUTHORIZATION=sender.request_header,
            HTTP_X_FORWARDED_FOR="1.2.3.4, 123.123.123.123",
        )

    expected = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Collection",
        "orderedItems": [
            {
                "id": "dit:domestic:HCSATFeedbackData:1:Update",
                "type": "Update",
                "object": {
                    "id": "dit:domestic:HCSATFeedbackData:1",
                    "type": "dit:domestic:HCSATFeedbackData",
                    "feedback_submission_date": "2012-01-14 12:00:01",
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
            },
            {
                "id": "dit:domestic:HCSATFeedbackData:2:Update",
                "type": "Update",
                "object": {
                    "id": "dit:domestic:HCSATFeedbackData:1",
                    "type": "dit:domestic:HCSATFeedbackData",
                    "feedback_submission_date": "2012-01-14 12:00:01",
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
            },
        ],
        "next": "http://testserver/activity-stream/v2/?after=1326542401.0_2",
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected
