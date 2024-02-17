from database import Base
from sqlalchemy import BLOB, Boolean, Column, DateTime, Integer, String


class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    username = Column(String(length=255), unique=True)
    email = Column(String(length=255), unique=True)
    about_me = Column(String(length=500))
    password = Column(String(length=255))
    registration_date = Column(DateTime)
    country = Column(Integer)  # ISO 3166-1 numeric
    picture = Column(BLOB)
    rating = Column(Integer)
    admin = Column(Boolean, nullable=False, default=False)
    disabled = Column(Boolean, nullable=False, default=False)
