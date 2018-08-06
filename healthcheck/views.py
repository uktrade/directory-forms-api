from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend


class DatabaseAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()


class PingAPIView(APIView):

    permission_classes = []
    http_method_names = ["get", ]

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
