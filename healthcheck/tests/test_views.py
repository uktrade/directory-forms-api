from unittest.mock import patch

from rest_framework import status

from django.core.urlresolvers import reverse


@patch(
    'health_check.db.backends.DatabaseBackend.check_status', return_value=True
)
def test_database(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:database'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1
