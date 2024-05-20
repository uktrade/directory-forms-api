from django.utils.decorators import decorator_from_middleware
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema)
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from activitystream.authentication import (
    ActivityStreamAuthentication, ActivityStreamHawkResponseMiddleware)
from activitystream.filters import SubmissionFilter
from activitystream.serializers import SubmissionSerializer
from submission.models import Submission

MAX_PER_PAGE = 25


class ActivityStreamView(ListAPIView):
    """List-only view set for the activity stream"""
    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()

    @staticmethod
    def _build_after(request, after_ts, after_id):
        return (
                request.build_absolute_uri(
                    reverse('activity-stream')
                ) + '?after={}_{}'.format(str(after_ts.timestamp()), str(after_id))
        )

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    @extend_schema(
        responses=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                'GET Request 200 Example',
                value={
                    '@context': 'list',
                    'type': 'Collection',
                    'orderedItems': 'list',
                    'next_page': 'url'
                },
                response_only=True,
            ),
        ],
        parameters=[OpenApiParameter(name='after', description='After Timestamp String', required=True, type=str)],
    )
    def list(self, request):
        """A single page of activities"""
        filter = SubmissionFilter(request.GET, queryset=Submission.objects.all())

        page_qs = filter.qs.order_by('created', 'id')[:MAX_PER_PAGE]
        items = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Collection',
            'orderedItems': SubmissionSerializer(page_qs, many=True).data
        }

        if not page_qs:
            next_page = {}
        else:
            last_submission = page_qs[len(page_qs)-1]
            next_page = {
                'next': self._build_after(
                    request, last_submission.created, last_submission.id)
            }

        return Response({
            **items,
            **next_page,
        })
