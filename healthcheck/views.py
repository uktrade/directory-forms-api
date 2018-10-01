from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend


class DatabaseAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()
