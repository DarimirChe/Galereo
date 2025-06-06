import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False, unique=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
