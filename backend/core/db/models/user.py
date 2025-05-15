from backend.core.db.session import Base
from sqlalchemy import BigInteger, String, Text, ForeignKey, Integer, Table, Column
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from enum import Enum
from sqlalchemy import Enum as SqlEnum

metadata = Base.metadata

class User(Base):

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), index=True,unique=True, nullable=False)
 
    hashed_password: Mapped[str] = mapped_column(Text, nullable=True)
    