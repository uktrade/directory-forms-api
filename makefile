ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

pytest:
	ENV_FILES='secrets-do-not-commit,test,dev' pytest $(ARGUMENTS)

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver 0.0.0.0:8011 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

secrets:
	@if [ ! -f ./conf/env/secrets-do-not-commit ]; \
		then sed -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' conf/env/secrets-template > conf/env/secrets-do-not-commit \
			&& echo "Created conf/env/secrets-do-not-commit"; \
		else echo "conf/env/secrets-do-not-commit already exists. Delete first to recreate it."; \
	fi

worker:
	ENV_FILES='secrets-do-not-commit,dev' celery -A conf worker -l info

.PHONY: clean pytest manage webserver requirements install_requirements css worker beat

build-docker:
	docker-compose -f docker-compose.test.yml build

up-docker:	
	docker-compose -f docker-compose.test.yml up

pytest-docker:
	docker-compose -f docker-compose.test.yml run --rm web pytest 

all-requirements-docker:
	docker-compose -f docker-compose.test.yml run --rm web pip-compile --output-file requirements.txt requirements.in
	docker-compose -f docker-compose.test.yml run --rm web pip-compile --output-file requirements_test.txt requirements_test.in

bash-docker:
	docker-compose -f docker-compose.test.yml run --rm web bash
	
shell-docker:
	docker-compose -f docker-compose.test.yml run --rm web python manage.py shell