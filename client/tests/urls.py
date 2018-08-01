from django.conf.urls import url

from django.views import View
from django.http.response import HttpResponse


class TestView(View):
    def get(self, *args, **kwargs):
        return HttpResponse()


urlpatterns = [
    url(
        r'^test/$',
        TestView.as_view(),
        name='test_view'
    ),
]
