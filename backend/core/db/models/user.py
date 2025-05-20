from backend.core.db.session import Base
from sqlalchemy import BigInteger, String, Text, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
import enum
from sqlalchemy import Enum as SqlEnum

metadata = Base.metadata


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    


class User(Base):

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), index=True,unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER, nullable=False)
 
    hashed_password: Mapped[str] = mapped_column(Text, nullable=True)

    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    wishlist: Mapped[List["Wishlist"]] = relationship(back_populates="user")
