from database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import BYTEA


class Users(Base):
    __tablename__ = "users"

    username = Column(String(length=32), primary_key=True)
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
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    white = Column(String(length=255))
    black = Column(String(length=255))
    moves = Column(BYTEA)


class Mistakes(Base):
    __tablename__ = "mistakes"

    id = Column(Integer, primary_key=True)
    fen = Column(String(length=127))
    moves = Column(BYTEA)
    rating = Column(Integer)


class Puzzles(Base):
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True)
    fen = Column(String(length=127))
    moves = Column(BYTEA)
    rating = Column(Integer)


class ThemeTags(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    tag_title = Column(String(length=255))


class Openings(Base):
    __tablename__ = "openings"

    id = Column(Integer, primary_key=True)
    eco = Column(BYTEA)
    name = Column(String(length=127))
    moves = Column(BYTEA)


PuzzleTheme = Table(
    "puzzle_theme",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("puzzle_id", Integer, ForeignKey("puzzles.id")),
    Column("theme_id", Integer, ForeignKey("themes.id")),
)

PuzzleOpening = Table(
    "puzzle_opening",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("puzzle_id", Integer, ForeignKey("puzzles.id")),
    Column("opening_id", Integer, ForeignKey("openings.id")),
)
