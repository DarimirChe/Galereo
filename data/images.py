import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Image(SqlAlchemyBase):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    path = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    prompt = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    like_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dislike_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_public = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
