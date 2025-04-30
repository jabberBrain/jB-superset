from flask_appbuilder.security.sqla.models import User
from sqlalchemy import (
    Column,
    String
)
class CustomUser(User):
    __tablename__ = "ab_user"
    solution_uuid = Column(String)
    jabberbrain_version = Column(String)
