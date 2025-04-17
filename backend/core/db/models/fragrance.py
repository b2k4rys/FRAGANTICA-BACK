from backend.core.db.session import Base
from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
from enum import Enum
from sqlalchemy import Enum as SqlEnum
metadata = Base.metadata


class FragranceType(Enum):
    edp = "Eau de Parfum"
    elixir = "Elixir"
    par = "Parfum"
    edt = "Eau de Toilette"

class Fragrance(Base):
    __tablename__ = "fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("company.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="fragrances")
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    fragrance_type: Mapped[FragranceType] = mapped_column(SqlEnum(FragranceType))


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)

    fragrances: Mapped[List[Fragrance]] = relationship(Fragrance, back_populates="company")



class Accord(Base):
    __tablename__ = "accord"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
