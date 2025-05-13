from backend.core.db.session import Base
from sqlalchemy import BigInteger, String, Text, ForeignKey, Integer, Table, Column
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


fragrance_accords_relationship = Table(
    "fragrance_accords_relationship",
    Base.metadata,
    Column("fragrance_id", ForeignKey("fragrance.id"), primary_key=True),
    Column("accord_id", ForeignKey("accord.id"), primary_key=True)
)

class Fragrance(Base):
    __tablename__ = "fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("company.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="fragrances")
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    fragrance_type: Mapped[FragranceType] = mapped_column(SqlEnum(FragranceType))
    ml: Mapped[int] = mapped_column(Integer,nullable=True)
    picture: Mapped[str] = mapped_column(String, nullable=True)

    accords: Mapped[List["Accord"]] = relationship(back_populates="fragrances", secondary=fragrance_accords_relationship)


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
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("accord_groups.id"), index = True)
    accord_group: Mapped["AccordGroup"] = relationship(back_populates="accords")

    fragrances: Mapped[List["Fragrance"]] = relationship(back_populates="accords", secondary=fragrance_accords_relationship)

    
class AccordGroup(Base):
    __tablename__ = "accord_groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    accords: Mapped[List["Accord"]] = relationship(back_populates="accord_group")

    
