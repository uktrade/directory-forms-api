from django.http.response import HttpResponse
from django.urls import re_path
from django.views import View


class TestView(View):
    def get(self, *args, **kwargs):
        return HttpResponse()


urlpatterns = [
    re_path(r"^test/$", TestView.as_view(), name="test_view"),
]
