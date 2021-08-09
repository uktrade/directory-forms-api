# sleep infinity

python /app/manage.py migrate
# Only run this in Non PROD environments
script="
from client.models import Client;

if Client.objects.filter(name='debug').count()==0:
    Client.objects.create(name='debug', identifier='12345678-1234-1234-1234-123456789012', access_key='01234567890123456789012345678912')
    print('debug client created.');
else:
    print('debug client creation skipped.');
"
printf "$script" | python manage.py shell

python /app/manage.py runserver 0.0.0.0:8011
