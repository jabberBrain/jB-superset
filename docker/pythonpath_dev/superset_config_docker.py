import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom"))

# This makes alembic run the db upgrade on our custom user
from superset.custom.models import CustomUser

AUTH_ROLE_PUBLIC = 'Public'
PUBLIC_ROLE_LIKE = 'Public'
FAB_API_SWAGGER_UI = True
APP_NAME = os.environ.get("APP_NAME", "jabberBrain Dashboards")
ENABLE_PROXY_FIX = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"

# Specify the App icon
APP_ICON = "/static/jb_assets/images/jB_logo_blue.svg"
LOGO_TARGET_PATH = os.getenv("LOGO_TARGET_PATH", "/")
FAVICONS = [{"href": "/static/jb_assets/images/jB_icon_blue.svg"}]

FEATURE_FLAGS : dict[str, bool] = {
    "DASHBOARD_RBAC": True,
    "ENABLE_TEMPLATE_PROCESSING": True, # Enables JINJA templating for SQLs
    "HORIZONTAL_FILTER_BAR": True,
    "DASHBOARD_ASYNC_QUERIES": True,     # kicks the queries off into Celery
    "DASHBOARD_NATIVE_FILTERS": True,
    "ALERT_REPORTS": True,
    "PLAYWRIGHT_REPORTS_AND_THUMBNAILS": True,
    "DATE_FORMAT_IN_EMAIL_SUBJECT": True
}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 1800,      # recycle idle connections every 30m
    "pool_pre_ping": True,     # avoid stale TCP connections
}

# Email configuration
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
SMTP_STARTTLS = os.environ.get("SMTP_TLS").lower() == "true"
SMTP_SSL_SERVER_AUTH = False
SMTP_SSL = os.environ.get("SMTP_SSL").lower() == "true"
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_MAIL_FROM = os.environ.get("SMTP_MAIL_FROM")
EMAIL_REPORTS_SUBJECT_PREFIX = os.environ.get("EMAIL_REPORTS_SUBJECT", "Report")


# Custom security manager
import logging
from superset.custom.security import CustomSecurityManager
from superset.custom.views import CustomIndexView
from flask import g
from celery.schedules import crontab

log = logging.getLogger(__name__)

CUSTOM_SECURITY_MANAGER=CustomSecurityManager
FAB_INDEX_VIEW = f"{CustomIndexView.__module__}.{CustomIndexView.__name__}"

GOOGLE_TAG_ID = os.getenv("GOOGLE_TAG_ID") or "no_google_id"
log.info("Google tag is: ", GOOGLE_TAG_ID)

# Custom macros
def current_user_solution_uuid():
    default_uuid = "no_solution"
    if g.user and hasattr(g.user, "solution_uuid"):
        return g.user.solution_uuid or default_uuid

    return default_uuid

JINJA_CONTEXT_ADDONS = {
    'current_user_solution_uuid': current_user_solution_uuid
}


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "0")

class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_concurrency = 4
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
    }
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }

SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# WebDriver configuration
# If you use Firefox, you can stick with default values
# If you use Chrome, then add the following WEBDRIVER_TYPE and WEBDRIVER_OPTION_ARGS

WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--force-device-scale-factor=2.0",
    "--high-dpi-support=2.0",
    "--headless",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-extensions",
]

# This is for internal use, you can keep http
WEBDRIVER_BASEURL = "http://superset_app:8088" # When running using docker compose use "http://superset_app:8088'
# This is the link sent to the recipient. Change to your domain, e.g. https://superset.mydomain.com
WEBDRIVER_BASEURL_USER_FRIENDLY = "https://www.stats.jabberbrain.com"

AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"

from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [
    {
        "name": "authentik",
        "token_key": "access_token",
        "icon": "fa-fingerprint",
        "remote_app": {
            "client_id": os.environ.get("AUTHENTIK_CLIENT_ID"),
            "client_secret": os.environ.get("AUTHENTIK_CLIENT_SECRET"),
            "client_kwargs": {
                "scope": "email openid profile entitlements virtual_assistants"
            },
            "server_metadata_url": os.environ.get("AUTHENTIK_CONF_URL")
        },
    }
]

CELERY_CONFIG = CeleryConfig
