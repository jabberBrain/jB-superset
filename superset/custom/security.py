import logging

from superset.security.manager import SupersetSecurityManager
from superset.custom.models import CustomUser
from superset.custom.views import CustomUserDBModelView

log = logging.getLogger(__name__)

class CustomSecurityManager(SupersetSecurityManager):
    user_model = CustomUser
    userdbmodelview = CustomUserDBModelView
