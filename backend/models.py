from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey


class Users(Base):
    __tablename__ = "users"

    username = Column(String(length=32), primary_key=True)
    email = Column(String(length=255), unique=True)
    about_me = Column(String(length=500))
    password = Column(String(length=125))
    registration_date = Column(DateTime)
    country = Column(String(length=2))  # ISO 3166-1 numeric
    picture = Column(BYTEA)
    admin = Column(Boolean, nullable=False, default=False)
    disabled = Column(Boolean, nullable=False, default=False)
    appearance: Mapped["Appearance"] = relationship(back_populates="users")


class Appearance(Base):
    __tablename__ = "appearance"

    username = mapped_column(ForeignKey("users.username"), primary_key=True)
    board = Column(String(length=32), nullable=False, default="blue")
    piece = Column(String(length=32), nullable=False, default="staunty")
    theme = Column(String(length=32), nullable=False, default="skeleton")
    dark = Column(Boolean, nullable=False, default=True)
    users: Mapped["Users"] = relationship(back_populates="appearance")


class Matches(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    white = Column(String(length=255))
    black = Column(String(length=255))
    moves = Column(BYTEA)
    winner = Column(Boolean)
    result = Column(SmallInteger)
    hyperchess = Column(Boolean)
    time = Column(SmallInteger)
    bonus = Column(SmallInteger)
    time_started = Column(DateTime)


class UserMatches(Base):
    __tablename__ = "user_matches"

    username = mapped_column(ForeignKey("users.username"), primary_key=True)
    matchId = mapped_column(ForeignKey("matches.id"), primary_key=True)
