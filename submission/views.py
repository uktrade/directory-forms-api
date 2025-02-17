from django.db import transaction
from django.http import Http404
from django.shortcuts import get_list_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from client.authentication import ClientSenderIdAuthentication
from submission import constants, helpers, serializers, tasks
from submission.models import Submission


class Ratelimited(Exception):
    pass


# API V1 - LEGACY


@extend_schema(methods=["POST"], description="Submit forms")
class SubmissionCreateAPIView(CreateAPIView):
    """
    This class represents the legacy V1 of the API. the /submission endpoint acted as a universal endpoint
    for all types of submissions (e.g. SMS, Email, Gov.Notify email). Going forward, any new services will be
    added a separate API endpoint, with a long term goal to decommission v1.
    """

    serializer_class = serializers.SubmissionModelSerializer
    authentication_classes = [ClientSenderIdAuthentication]

    def perform_ratelimit_check(self, submission):
        if helpers.is_ratelimited(submission.ip_address):
            submission.sender.blacklist(reason=constants.IP_RESTRICTED)
            raise Ratelimited

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.perform_ratelimit_check(serializer.instance)
        tasks.execute_for_submission(serializer.instance)

    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return Response(status=429)
        if isinstance(exc, AuthenticationFailed):
            return Response(status=exc.status_code)
        return super().handle_exception(exc)


class SubmissionDestroyAPIView(SubmissionCreateAPIView, DestroyAPIView):
    """
    Deletes all entries for a particular email within directory-forms-api.
    """

    def delete(self, request, **kwargs):
        email_address = kwargs["email_address"]
        try:
            submission_instances = get_list_or_404(
                Submission,
                sender__email_address=email_address,
            )
            for submission in submission_instances:
                submission.delete()
        except Http404:
            pass

        return Response(status=204)


# API V2
class APIBase(APIView):
    """
    Base class for the V2 API.
    """

    authentication_classes = [ClientSenderIdAuthentication]


@extend_schema(methods=["POST"], description="Gov.notify Bulk Email")
class GovNotifyBulkEmailAPIView(APIBase):
    """
    This endpoint accepts emails submissions for Gov.notify. It is capable of accepting single or bulk
    submissions (where the same email is to be sent to multiple recipients).
    """

    def post(self, request):
        """
        Acts as a wrapper for SubmissionModelSerializer, taking email data is a list of dicts ('bulk_email_entries')
        and calling the SubmissionModelSerializer for each, saving a Submission entry in the DB. This is picked up by
        a scheduled task for email delivery.

        POST request data params:
        template_id: The gov.notify email template id to be used for the email.
        bulk_email_entries: List of dicts representing email data. MUST have an 'email_address' key.
        email_reply_to_id: Reply to email (optional).
        """

        serializer = serializers.GovNotifyBulkEmailSerializer(data=request.data)
        if serializer.is_valid():
            # Create a submission entry for each entry in the bulk_email_entries dict submitted
            with transaction.atomic():
                # We use request.data rather than serializer.data here to retain unknown dict keys
                # that would otherwise be removed by the GovNotifyBulkEmailEntrySerializer.
                for entry in request.data["bulk_email_entries"]:
                    submission_data = {
                        "data": entry,
                        "meta": {
                            "action_name": constants.ACTION_NAME_GOV_NOTIFY_BULK_EMAIL,
                            "template_id": serializer.data["template_id"],
                            "email_address": entry["email_address"],
                        },
                    }

                    submission = serializers.SubmissionModelSerializer(
                        data=submission_data, context={"request": request}
                    )
                    if submission.is_valid(raise_exception=True):
                        submission.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(methods=["POST"], description="HCSat Feedback Bulk Submission")
class HCSatAPIView(APIBase):

    def post(self, request):
        serializer = serializers.HCSatSerializer(data=request.data)
        if serializer.is_valid():
            # Create a submission entry for each entry in the hcsat_feedback_entries dict submitted
            with transaction.atomic():
                for entry in request.data["hcsat_feedback_entries"]:
                    submission_data = {
                        "data": entry,
                        "meta": {
                            "action_name": constants.ACTION_NAME_HCSAT_SUBMISSION,
                        },
                    }

                    submission = serializers.SubmissionModelSerializer(
                        data=submission_data, context={"request": request}
                    )
                    if submission.is_valid(raise_exception=True):
                        submission.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
