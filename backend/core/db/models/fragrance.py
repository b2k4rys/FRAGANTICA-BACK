from backend.core.db.session import Base
from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List
metadata = Base.metadata

class Fragrance(Base):
    __tablename__ = "fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("company.id"), nullable=False)
    company: Mapped["Company"] = relationship("Company", back_populates="fragrances")
   


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
