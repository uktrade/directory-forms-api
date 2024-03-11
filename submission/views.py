from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

from submission import constants, helpers, serializers, tasks
from client.authentication import ClientSenderIdAuthentication
from django.shortcuts import get_list_or_404
from submission.models import Submission


class Ratelimited(Exception):
    pass

# API V1 - LEGACY

@extend_schema(methods=['POST'], description='Submit forms')
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
        return super().handle_exception(exc)


class SubmissionDestroyAPIView(SubmissionCreateAPIView, DestroyAPIView):
    """
    Deletes all entries for a particular email within directory-forms-api.
    """
    def delete(self, request, **kwargs):
        email_address = kwargs['email_address']
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
class APIV2Base(APIView):
    """
    Base class for the V2 API.
    """

    authentication_classes = [ClientSenderIdAuthentication]

    def perform_ratelimit_check(self, submission):
        if helpers.is_ratelimited(submission.ip_address):
            submission.sender.blacklist(reason=constants.IP_RESTRICTED)
            raise Ratelimited

    def handle_exception(self, exc):
        if isinstance(exc, Ratelimited):
            return Response(status=429)
        return super().handle_exception(exc)


@extend_schema(methods=['POST'], description='Gov.notify Bulk Email')
class GovNotifyBulkEmailAPIView(APIV2Base):
    """
    This endpoint accept a bulk email submission for Gov.notify where the same email is to be sent to multiple
    recipients.
    """

    def post(self, request):
        """
        Acts as a wrapper for GovNotifyEmailSerializer, taking a list of email addresses and calling the
        GovNotifyEmailSerializer for each, saving a Submission entry in the DB.
        """

        serializer = serializers.GovNotifyBulkEmailSerializer(data=request.data)
        if serializer.is_valid():
            # Create a submission entry for each email
            for email_address in serializer.email_addresses:
                request.data.email_address = email_address
                submission = serializers.GovNotifyEmailSerializer(data=request.data)
                submission.is_valid(raise_exception=True)
                submission.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


