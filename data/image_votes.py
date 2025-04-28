import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class ImageVote(SqlAlchemyBase):
    __tablename__ = 'image_votes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    image_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("images.id"), nullable=False)
    vote = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
