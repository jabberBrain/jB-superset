import logging
from superset.security.manager import SupersetSecurityManager
from superset.custom.models import CustomUser
from superset.custom.views import CustomUserDBModelView, CustomSsoAuthOAuthView
from superset import db

log = logging.getLogger(__name__)

class CustomSecurityManager(SupersetSecurityManager):
    user_model = CustomUser
    userdbmodelview = CustomUserDBModelView
    useroauthmodelview = CustomUserDBModelView
    authoauthview = CustomSsoAuthOAuthView

    def oauth_user_info(self, provider, response=None):
        log.debug("OAuth2 provider: %s.", provider)
        user = self.appbuilder.sm.oauth_remotes[provider].userinfo()
        log.info("Parsed user data: %s", user)

        virtual_assistants = user.get("virtual_assistants", [])
        solution_uuid = "(" + ",".join("'" + va + "'" for va in virtual_assistants) + ")"
        name = user.get("name", "")
        name_parts = name.strip().split() if name else []
        first_name = name_parts[0] if name_parts else user.get("email", "")
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        roles = user.get("roles", [])

        # Extract required fields from userinfo
        return {
            "email": user.get("email", ""),
            "username": user.get("email", ""),
            "first_name": first_name,
            "last_name": last_name,
            "solution_uuid": solution_uuid,
            "roles": roles
        }

    def create_new_user(self, userinfo):
        username = userinfo.get("username")
        email = userinfo.get("email")
        first_name = userinfo.get("first_name")
        last_name = userinfo.get("last_name")
        return self.add_user(username, first_name, last_name, email, role=self.find_role('Public'))

    def auth_user_oauth(self, userinfo):
        log.info(f"Processing OAuth for user: {userinfo}")
        user = self.find_user(email=userinfo.get("email"))
        log.info(f"User search returned: {user}")
        if not user:
            log.info(f"Creating new user for {userinfo.get('email')}")
            user = self.create_new_user(userinfo)

        user.username = userinfo.get("username", user.username)
        user.email = userinfo.get("email", user.email)
        user.first_name = userinfo.get("first_name", user.first_name)
        user.last_name = userinfo.get("last_name", user.last_name)
        user.solution_uuid = userinfo.get("solution_uuid", "")

        user.roles = [ role
            for role in (
                self.find_role(rn) for rn in userinfo.get("roles", [])
            ) if role
        ]

        self.update_user(user)
        return user
