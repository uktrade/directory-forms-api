clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py distributed_migrate --noinput
FLAKE8 := flake8 . --exclude=migrations,.venv --max-line-length=120
PYTEST := pytest . --cov=. --capture=no --cov-config=.coveragerc $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput; \
	python manage.py distributed_migrate --noinput; \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DEBUG_SET_ENV_VARS := \
	export SECRET_KEY=debug; \
	export PORT=8011; \
	export DEBUG=true; \
	export DB_NAME=directory_forms_api_debug; \
	export DB_USER=debug; \
	export DB_PASSWORD=debug; \
	export DATABASE_URL=postgres://debug:debug@localhost:5432/directory_forms_api_debug; \
	export HEALTH_CHECK_TOKEN=debug; \
	export CSRF_COOKIE_SECURE=false; \
	export SESSION_COOKIE_SECURE=false; \
	export SESSION_COOKIE_DOMAIN=.trade.great; \
	export DEFAULT_FROM_EMAIL=debug@example.com; \
	export FEATURE_ENFORCE_STAFF_SSO_ENABLED=false; \
	export REDIS_CELERY_URL=redis://127.0.0.1:6379; \
	export CELERY_ALWAYS_EAGER=true

TEST_SET_ENV_VARS := \
	export ZENDESK_EMAIL=debug@example.com; \
	export ZENDESK_SUBDOMAIN=example; \
	export ZENDESK_TOKEN=some-token; \
	export ZENDESK_CUSTOM_FIELD_ID=123455; \
	export GOV_NOTIFY_API_KEY=7891011; \
	export GOV_NOTIFY_LETTER_API_KEY=1101987; \
	export ZENDESK_SUBDOMAIN_EUEXIT=example-euexit; \
	export ZENDESK_TOKEN_EUEXIT=some-token-euexit; \
	export ZENDESK_EMAIL_EUEXIT=debug@example.com; \
	export ZENDESK_CUSTOM_FIELD_ID_EUEXIT=94393; \
	export EMAIL_HOST=debug; \
	export EMAIL_HOST_PASSWORD=debug; \
	export EMAIL_HOST_USER=debug@example.com; \
	export EMAIL_USE_TLS=true

debug_celery_worker:
	$(DEBUG_SET_ENV_VARS); celery -A conf worker -l info

debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER)

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations

debug: test_requirements debug_db debug_test

compile_requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

upgrade_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements_test.in

.PHONY: build clean test_requirements debug_webserver debug_db debug_test debug heroku_deploy_dev smoke_tests compile_all_requirements