from django.http import Http404
from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from submission.models import Submission


class TestAPIView(GenericAPIView):

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLED:
            raise Http404
        return super().dispatch(*args, **kwargs)


class SubmissionsTestAPIView(TestAPIView):
    queryset = Submission.objects.all()
    permission_classes = []
    http_method_names = 'get'

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
            if submission.meta['action_name'] == 'pardot':
                if submission.data['email'] == email_address:
                    results.append(self.data_and_meta(submission))
            if submission.meta['action_name'] in ['gov-notify', 'zendesk']:
                if submission.meta['email_address'] == email_address:
                    results.append(self.data_and_meta(submission))
            if submission.meta['action_name'] == 'email':
                if email_address in submission.meta['recipients']:
                    results.append(self.data_and_meta(submission))
        return results

    def get(self, request, *args, **kwargs):
        email_address = kwargs['email_address']
        meta = self.get_submissions(email_address)
        return Response(meta) if meta else Response(status=404)
