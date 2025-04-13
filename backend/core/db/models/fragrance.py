from backend.core.db.session import Base
from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy.orm import mapped_column, Mapped
metadata = Base.metadata

class Fragrance(Base):
    __tablename__ = "fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    company: Mapped["Company"] = mapped_column()



class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)



class Accord(Base):
    __tablename__ = "accord"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
