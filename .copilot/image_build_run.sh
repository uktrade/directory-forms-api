#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# create temp values for env values
export zendesk_token_euexit=""
export zendesk_email_euexit=""
export zendesk_custom_field_id_euexit=""
export email_host=""
export email_host_user=""
export email_host_password=""
export default_from_email=""
export gov_notify_api_key=""
export gov_notify_letter_api_key=""
export activity_stream_access_key_id=""
export activity_stream_secret_access_key=""
export database_url=""
# Add commands below to run inside the container after all the other buildpacks have been applied
python manage.py collectstatic --noinput