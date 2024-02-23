from database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import BYTEA


class Users(Base):
    __tablename__ = "Users"

    username = Column(String(length=255), primary_key=True)
    email = Column(String(length=255), unique=True)
    about_me = Column(String(length=500))
    password = Column(String(length=255))
    registration_date = Column(DateTime)
    country = Column(Integer)  # ISO 3166-1 numeric
    picture = Column(BYTEA)
    rating = Column(Integer)
    admin = Column(Boolean, nullable=False, default=False)
    disabled = Column(Boolean, nullable=False, default=False)


class Matches(Base):
    __tablename__ = "Matches"

    match_id = Column(Integer, primary_key=True)
    white = Column(String(length=255))
    black = Column(String(length=255))
    moves = Column(BYTEA)
