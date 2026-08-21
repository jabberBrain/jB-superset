import logging
from superset.security.manager import SupersetSecurityManager
from superset.custom.models import CustomUser
from superset.custom.views import CustomUserDBModelView, CustomSsoAuthOAuthView
from superset.custom.role_ownership import decide_role_sync
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

        # ⛔ Authentik SEEDS the roles; it does not own them.
        #
        # This used to be an unconditional `user.roles = [...]` on every single
        # login, so a role set in Superset was reverted the next time the person
        # signed in — and once jBKB writes roles here, it would revert those too.
        # AIM had the same line and it was watched happen live.
        #
        # PHASE 1 OF TWO: the seed goes away as well, once the role data is
        # curated in jBKB and jBKB creates the account itself. See
        # superset/custom/role_ownership.py.
        token_roles = [rn for rn in userinfo.get("roles", []) if rn]
        stored_roles = [r.name for r in (user.roles or [])]
        decision = decide_role_sync(stored_roles, token_roles)

        if decision == "adopt":
            resolved = [r for r in (self.find_role(rn) for rn in token_roles) if r]
            # find_role returns None for a role that does not exist in Superset.
            # Adopting the empty remainder would leave the user with no roles at
            # all, so keep what they have and say which names did not resolve.
            if resolved:
                user.roles = resolved
            else:
                log.warning(
                    "Insight Hub: none of the Authentik roles %s exist in Superset; "
                    "leaving %s as %s.",
                    token_roles, user.email, stored_roles or ["(none)"],
                )
        elif decision == "diverged":
            # Expected the moment an administrator changes a role. Information,
            # not a fault — but worth being able to find in the log later.
            log.info(
                "Insight Hub: keeping stored roles %s for %s; Authentik offered %s.",
                stored_roles, user.email, token_roles,
            )

        self.update_user(user)
        return user
