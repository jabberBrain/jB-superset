import logging
from flask_appbuilder.security.views import UserDBModelView, UserOAuthModelView
from flask_babel import lazy_gettext
from flask_appbuilder import expose, IndexView
from flask import redirect, g, url_for
from superset.superset_typing import FlaskResponse
from superset.utils.core import (
    get_user_id,
)
from superset import security_manager

log = logging.getLogger(__name__)

class CustomUserDBModelView(UserDBModelView, UserOAuthModelView):
    """
    View that adds DB specifics to User view. Override to implement your own custom view.
    Then override userdbmodelview property on SecurityManager.
    """
    user_show_fieldsets = [
        (
            lazy_gettext('User info'),
            {'fields': ['username', 'first_name', 'last_name', 'email']}
        ),
    ]

    label_columns = UserDBModelView.label_columns
    label_columns["solution_uuid"] = lazy_gettext("Virtual Assistant Id")

    add_columns = UserDBModelView.add_columns
    add_columns.append('solution_uuid')

    list_columns = UserDBModelView.list_columns
    list_columns.append('solution_uuid')

    edit_columns = UserDBModelView.edit_columns
    edit_columns.append('solution_uuid')

    search_columns = UserDBModelView.search_columns
    edit_columns.append('solution_uuid')

WELCOME_PAGE_REDIRECT_ADMIN="Superset.welcome"
WELCOME_PAGE_REDIRECT_DEFAULT="DashboardModelView.list"

class CustomIndexView(IndexView):
    @expose("/")
    def index(self) -> FlaskResponse:
        if not g.user or not get_user_id():
            return redirect(url_for("AuthOAuthView.login", provider="authentik"))
        if security_manager.is_admin():
            return redirect(url_for(WELCOME_PAGE_REDIRECT_ADMIN))
        
        return redirect(url_for(WELCOME_PAGE_REDIRECT_DEFAULT))
