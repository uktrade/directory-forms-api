from django.http import Http404
from django.conf import settings
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from client.authentication import ClientSenderIdAuthentication
from submission.models import Submission
from submission.constants import (
    ACTION_NAME_EMAIL,
    ACTION_NAME_GOV_NOTIFY_EMAIL,
    ACTION_NAME_PARDOT,
    ACTION_NAME_ZENDESK,
)


class SubmissionsTestAPIView(RetrieveAPIView):
    queryset = Submission.objects.all()
    authentication_classes = [ClientSenderIdAuthentication]
    http_method_names = 'get'

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)

    @staticmethod
    def data_and_meta(submission: Submission):
        return {
            'data': dict(submission.data),
            'meta': dict(submission.meta),
            'is_sent': submission.is_sent,
            'form_url': submission.form_url,
        }

    def get_submissions(self, email_address):
        results = []
        for submission in self.queryset.all():
            if submission.meta['action_name'] == ACTION_NAME_PARDOT:
                if submission.data['email'] == email_address:
                    results.append(self.data_and_meta(submission))
            if submission.meta['action_name'] in [ACTION_NAME_GOV_NOTIFY_EMAIL, ACTION_NAME_ZENDESK]:
                if submission.meta['email_address'] == email_address:
                    results.append(self.data_and_meta(submission))
            if submission.meta['action_name'] == ACTION_NAME_EMAIL:
                if email_address in submission.meta['recipients']:
                    results.append(self.data_and_meta(submission))
        return results

    def get(self, request, *args, **kwargs):
        email_address = kwargs['email_address']
        meta = self.get_submissions(email_address)
        return Response(meta) if meta else Response(status=404)
