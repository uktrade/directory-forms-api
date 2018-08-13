build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

DJANGO_MIGRATE := python manage.py distributed_migrate --noinput
FLAKE8 := flake8 . --exclude=migrations,.venv
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

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := python docker/env_writer.py docker/env.json docker/env-postgres.json
DOCKER_COMPOSE_CREATE_TEST_ENVS := python docker/env_writer.py docker/env.test.json docker/env-postgres.test.json

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export DIRECTORY_FORMS_API_PORT=8011; \
	export directory_forms_api_debug=true; \
	export DIRECTORY_FORMS_API_SECRET_KEY=debug; \
	export DIRECTORY_FORMS_API_POSTGRES_USER=debug; \
	export DIRECTORY_FORMS_API_POSTGRES_PASSWORD=debug; \
	export DIRECTORY_FORMS_API_POSTGRES_DB=directory_forms_api_debug; \
	export DIRECTORY_FORMS_API_DATABASE_URL=postgres://debug:debug@postgres:5432/directory_forms_api_debug; \
	export DIRECTORY_FORMS_API_HEALTH_CHECK_TOKEN=debug; \
	export DIRECTORY_FORMS_API_CSRF_COOKIE_SECURE=false; \
	export DIRECTORY_FORMS_API_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_FORMS_API_SESSION_COOKIE_DOMAIN=.trade.great; \
	export DIRECTORY_FORMS_API_DEFAULT_FROM_EMAIL=debug@example.com


docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_TEST_ENVS)

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep -e directoryapi_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run -d --no-deps celery_beat_scheduler && \
	docker-compose run -d --no-deps celery_worker && \
	docker-compose run --service-ports webserver make django_webserver

debug_test_last_failed:
	make debug_test pytest_args='--last-failed'

docker_webserver_bash:
	docker exec -it directoryapi_webserver_1 sh

docker_psql:
	docker-compose run postgres psql -h postgres -U debug

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_CREATE_TEST_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

docker_build:
	docker build -t ukti/directory-forms-api:latest .

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
	export DEFAULT_FROM_EMAIL=debug@example.com


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
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_MIGRATE) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations

debug: test_requirements debug_db debug_test


heroku_deploy_dev:
	./docker/install_heroku_cli.sh
	docker login --username=$$HEROKU_EMAIL --password=$$HEROKU_TOKEN registry.heroku.com
	~/bin/heroku-cli/bin/heroku container:push --recursive --app directory-forms-api-dev
	~/bin/heroku-cli/bin/heroku container:release web --app directory-forms-api-dev

compile_requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

upgrade_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements_test.in

.PHONY: build docker_run_test clean test_requirements docker_run docker_debug docker_webserver_bash docker_psql docker_test debug_webserver debug_db debug_test debug heroku_deploy_dev smoke_tests compile_all_requirements
