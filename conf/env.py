from typing import Any, Optional

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.utility import is_copilot
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from conf.helpers import get_env_files, is_circleci, is_local


class BaseSettings(PydanticBaseSettings):
    """Base class holding all environment variables for Great."""

    model_config = SettingsConfigDict(
        extra="ignore",
        validate_default=False,
    )

    # Start of Environment Variables
    debug: bool = False
    app_environment: str = "dev"
    static_host: str = ""
    staticfiles_storage: str = "whitenoise.storage.CompressedStaticFilesStorage"
    sentry_dsn: str = ""
    secret_key: str

    sentry_environment: str = ""
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 1.0
    feature_enforce_staff_sso_enabled: bool = False

    staff_sso_authbroker_url: str
    authbroker_client_id: str
    authbroker_client_secret: str

    elastic_apm_enabled: bool = False

    service_name: str = "directory-forms-api"
    environment: str = app_environment
    elastic_apm_secret_token: str
    elastic_apm_url: str
    elastic_apm_server_timeout: str = "20s"

    feature_openapi_enabled: bool = False

    session_cookie_domain: str = "great.gov.uk"
    session_cookie_secure: bool = True
    csrf_cookie_secure: bool = True

    health_check_token: str

    zendesk_subdomain: str
    zendesk_subdomain_euexit: str
    zendesk_token: str
    zendesk_email: str
    zendesk_custom_field_id: str

    zendesk_token_euexit: str
    zendesk_email_euexit: str
    zendesk_custom_field_id_euexit: str

    email_backend_class_name: str = "default"

    email_host: str
    email_port: int = 587
    email_host_user: str
    email_host_password: str
    email_use_tls: bool = True
    default_from_email: str

    feature_redis_use_ssl: bool = False
    celery_always_eager: bool = True

    gov_notify_api_key: str
    buy_from_uk_enquiry_template_id: str = "b3212b30-6321-46e7-9dba-ad37bd92df89"
    buy_from_uk_email_address: str = "enquiries@invest-trade.uk"
    buy_from_uk_reply_to_email_address: str = "c071d4f6-94a7-4afd-9acb-6b164737731c"
    gov_notify_letter_api_key: str

    feature_test_api_enabled: bool = False

    activity_stream_access_key_id: str
    activity_stream_secret_access_key: str

    ratelimit_rate: str = "15/h"

    submission_filter_hours: int = 72


class CIEnvironment(BaseSettings):

    database_url: str
    redis_url: str = ""


class DBTPlatformEnvironment(BaseSettings):
    """Class holding all listed environment variables on DBT Platform.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. DBTPlatformEnvironment.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    build_step: bool = False
    redis_endpoint: str = ""

    @computed_field(return_type=str)
    @property
    def database_url(self):
        return database_url_from_env("DATABASE_CREDENTIALS")

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        return self.redis_endpoint


class GovPaasEnvironment(BaseSettings):
    """Class holding all listed environment variables on Gov PaaS.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. GovPaasSettings.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    class VCAPServices(BaseModel):
        """Config of services bound to the Gov PaaS application"""

        model_config = ConfigDict(extra="ignore")

        postgres: list[dict[str, Any]]
        redis: list[dict[str, Any]]

    class VCAPApplication(BaseModel):
        """Config of the Gov PaaS application"""

        model_config = ConfigDict(extra="ignore")

        application_id: str
        application_name: str
        application_uris: list[str]
        cf_api: str
        limits: dict[str, Any]
        name: str
        organization_id: str
        organization_name: str
        space_id: str
        uris: list[str]

    model_config = ConfigDict(extra="ignore")

    vcap_services: Optional[VCAPServices] = None
    vcap_application: Optional[VCAPApplication] = None

    @computed_field(return_type=str)
    @property
    def database_url(self):
        if self.vcap_services:
            return self.vcap_services.postgres[0]["credentials"]["uri"]

        return "postgres://"

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        if self.vcap_services:
            return self.vcap_services.redis[0]["credentials"]["uri"]

        return "rediss://"


if is_local() or is_circleci():
    # Load environment files in a local or CI environment
    env = CIEnvironment(_env_file=get_env_files(), _env_file_encoding="utf-8")
elif is_copilot():
    # When deployed read values from DBT Platform environment
    env = DBTPlatformEnvironment()
else:
    # When deployed read values from Gov PaaS environment
    env = GovPaasEnvironment()
