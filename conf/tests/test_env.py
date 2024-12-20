import json
import os
from importlib import reload

import environ
import pytest

# from config.env import DBTPlatformEnvironment, GovPaasEnvironment, env
from conf import env as environment_reader


@pytest.fixture
def environment():
    env = environ.Env()
    for env_file in env.list("ENV_FILES", default=[]):
        env.read_env(f"conf/env/{env_file}")


@pytest.fixture
def vcap_services():
    data = {
        "postgres": [
            {
                "binding_guid": "123",
                "binding_name": None,
                "credentials": {
                    "host": "example.com",
                    "jdbcuri": "jdbc:postgresql://example.com:5432/exampledb",
                    "name": "exampledb",
                    "password": "examplepassword",
                    "port": 5432,
                    "uri": "postgres://exampleuser:examplepassword@example.com:5432/exampledb",
                    "username": "exampleuser",
                },
                "instance_guid": "1234",
                "instance_name": "directory-forms-api-db",
                "label": "postgres",
                "name": "directory-forms-api-db",
                "plan": "medium-ha",
                "provider": None,
                "syslog_drain_url": None,
                "tags": ["postgres", "relational"],
                "volume_mounts": [],
            }
        ],
        "redis": [
            {
                "binding_guid": "456",
                "binding_name": None,
                "credentials": {
                    "host": "example.com",
                    "name": "exampleuser",
                    "password": "examplepassword",
                    "port": 6379,
                    "tls_enabled": True,
                    "uri": "rediss://examplepassword@example.com:6379",
                },
                "instance_guid": "4567",
                "instance_name": "directory-forms-api-redis-small",
                "label": "redis",
                "name": "directory-forms-api-redis-small-ha-6",
                "plan": "small-ha",
                "provider": None,
                "syslog_drain_url": None,
                "tags": ["elasticache", "redis"],
                "volume_mounts": [],
            }
        ],
    }
    return json.dumps(data)


@pytest.fixture
def vcap_application():
    data = {
        "application_id": "12345",
        "application_name": "directory-forms-api",
        "application_uris": ["www.example.com"],
        "cf_api": "https://api.example.com",
        "limits": {"fds": 1},
        "name": "directory-forms-api",
        "organization_id": "67890",
        "organization_name": "example-org",
        "space_id": "98765",
        "space_name": "example-space",
        "uris": ["www.example.com"],
        "users": None,
    }
    return json.dumps(data)


@pytest.fixture
def database_credentials():
    data = {
        "engine": "postgres",
        "username": "exampleuser",
        "password": "examplepassword",
        "dbname": "exampledb",
        "host": "example.com",
        "port": 5432,
    }
    return json.dumps(data)


def test_gov_paas_environment(vcap_application, vcap_services, environment):
    os.environ.pop("IS_CIRCLECI", None)
    os.environ["APP_ENVIRONMENT"] = "local"
    os.environ["VCAP_SERVICES"] = vcap_services
    os.environ["VCAP_APPLICATION"] = vcap_application

    reload(environment_reader)

    os.environ["IS_CIRCLECI"] = "false"

    assert isinstance(environment_reader.env, environment_reader.GovPaasEnvironment)
    assert environment_reader.env.app_environment == "local"
    assert environment_reader.env.secret_key == "debug"
    assert (
        environment_reader.env.database_url
        == "postgres://exampleuser:examplepassword@example.com:5432/exampledb"
    )
    assert (
        environment_reader.env.redis_url == "rediss://examplepassword@example.com:6379"
    )
    assert environment_reader.env.vcap_application.name == "directory-forms-api"

    environment_reader.env.vcap_services = None

    assert environment_reader.env.database_url == "postgres://"
    assert environment_reader.env.redis_url == "rediss://"


def test_dbt_platform_environment(database_credentials, environment):
    os.environ.pop("IS_CIRCLECI", None)
    os.environ["APP_ENVIRONMENT"] = "local"
    os.environ["COPILOT_ENVIRONMENT_NAME"] = "test"
    os.environ["DATABASE_CREDENTIALS"] = database_credentials
    os.environ["REDIS_ENDPOINT"] = "rediss://examplepassword@example.com:6379"

    reload(environment_reader)

    os.environ["IS_CIRCLECI"] = "false"

    assert isinstance(environment_reader.env, environment_reader.DBTPlatformEnvironment)
    assert environment_reader.env.app_environment == "local"
    assert environment_reader.env.secret_key == "debug"
    assert (
        environment_reader.env.database_url
        == "postgres://exampleuser:examplepassword@example.com:5432/exampledb"
    )
    assert (
        environment_reader.env.redis_url == "rediss://examplepassword@example.com:6379"
    )


def test_ci_environment():
    os.environ["DATABASE_URL"] = (
        "postgres://exampleuser:examplepassword@example.com:5432/exampledb"
    )
    os.environ["REDIS_URL"] = "rediss://examplepassword@example.com:6379"

    reload(environment_reader)

    assert isinstance(environment_reader.env, environment_reader.CIEnvironment)
    assert environment_reader.env.app_environment == "local"
    assert environment_reader.env.secret_key == "debug"
    assert (
        environment_reader.env.database_url
        == "postgres://exampleuser:examplepassword@example.com:5432/exampledb"
    )
    assert (
        environment_reader.env.redis_url == "rediss://examplepassword@example.com:6379"
    )
