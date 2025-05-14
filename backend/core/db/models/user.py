from backend.core.db.session import Base
from sqlalchemy import BigInteger, String, Text, ForeignKey, Integer, Table, Column
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from enum import Enum
from sqlalchemy import Enum as SqlEnum

class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), index=True)

    name: Mapped[str] = mapped_column(String(150))
    surname: Mapped[str] = mapped_column(String(150))
    