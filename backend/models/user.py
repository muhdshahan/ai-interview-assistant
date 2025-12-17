""" Setting user model """

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from backend.db.database import Base
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column(String)