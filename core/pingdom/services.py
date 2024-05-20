from django.db import DatabaseError

from submission.models import Submission


class DatabaseHealthCheck:
    name = 'database'

    def check(self):
        try:
            Submission.objects.all().exists()
        except DatabaseError as de:
            return False, de
        else:
            return True, ''


health_check_services = (DatabaseHealthCheck,)