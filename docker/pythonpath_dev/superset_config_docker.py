import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom"))

# This makes alembic run the db upgrade on our custom user
from superset.custom.models import CustomUser

AUTH_ROLE_PUBLIC = 'Public'
PUBLIC_ROLE_LIKE = 'Public'
FAB_API_SWAGGER_UI = False
APP_NAME = os.environ.get("APP_NAME", "jabberBrain Dashboards")
ENABLE_PROXY_FIX = True

# Specify the App icon
APP_ICON = "/static/jb_assets/images/jB_logo_blue.svg"
LOGO_TARGET_PATH = "/"
FAVICONS = [{"href": "/static/jb_assets/images/jB_icon_blue.svg"}]

FEATURE_FLAGS : dict[str, bool] = {
    "DASHBOARD_RBAC": True,
    "ENABLE_TEMPLATE_PROCESSING": True, # Enables JINJA templating for SQLs
    "HORIZONTAL_FILTER_BAR": True,
    "DASHBOARD_ASYNC_QUERIES": True,     # kicks the queries off into Celery
    "DASHBOARD_NATIVE_FILTERS": True
}

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 1800,      # recycle idle connections every 30m
    "pool_pre_ping": True,     # avoid stale TCP connections
}

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

def current_user_jabberbrain_version():
    default_version = "1"
    if g.user and hasattr(g.user, "jabberbrain_version"):
        return g.user.jabberbrain_version or default_version
    
    return default_version

JINJA_CONTEXT_ADDONS = {
    'current_user_solution_uuid': current_user_solution_uuid,
    'current_user_jabberbrain_version': current_user_jabberbrain_version
}


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_concurrency = 4
    worker_prefetch_multiplier = 1
    task_acks_late = True
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig