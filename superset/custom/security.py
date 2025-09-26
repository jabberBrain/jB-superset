import logging

from superset.security.manager import SupersetSecurityManager
from superset.custom.models import CustomUser
from superset.custom.views import CustomUserDBModelView
from superset import db

from superset.security import SupersetSecurityManager
log = logging.getLogger(__name__)

class CustomSecurityManager(SupersetSecurityManager):
    user_model = CustomUser
    userdbmodelview = CustomUserDBModelView

    def oauth_user_info(self, provider, response=None):
        log.debug("Oauth2 provider: {0}.".format(provider))
        if provider == 'authentik':
            me = self.appbuilder.sm.oauth_remotes[provider].get('userinfo')
            log.info("Displaying user data")
            log.info("user_data: %s", me)
            return { 'name' : me['name'], 'email' : me['email'], 'id' : me['user_name'], 'username' : me['user_name'], 'first_name':'', 'last_name':''}

