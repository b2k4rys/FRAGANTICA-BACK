from backend.core.db.session import Base
from sqlalchemy import BigInteger, String, Text, ForeignKey, Integer, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from typing import List
from enum import Enum
from sqlalchemy import Enum as SqlEnum
metadata = Base.metadata


class FragranceType(Enum):
    edp = "Eau de Parfum"
    elixir = "Elixir"
    par = "Parfum"
    edt = "Eau de Toilette"

class WishListType(Enum):
    OWNED = "owned"
    WANTED = "wanted"
    USED = "used"

class NoteType(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BASE = "base"



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
    fragrance_reviews: Mapped[List["Review"]] = relationship(back_populates="fragrance")

    users: Mapped[List["Wishlist"]] = relationship(back_populates="fragrance")
    notes: Mapped[List["FragranceNote"]] = relationship(back_populates="fragrance")


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)

    fragrances: Mapped[List[Fragrance]] = relationship(Fragrance, back_populates="company")


class Note(Base):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("note_group.id"), index = True)
    category: Mapped["NoteGroup"] = relationship(back_populates="note")

    fragrances: Mapped[List["FragranceNote"]] = relationship(back_populates="note")

    
class NoteGroup(Base):
    __tablename__ = "note_group"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    note: Mapped[List["Note"]] = relationship(back_populates="category")

    
class FragranceNote(Base):
    __tablename__ = "fragrance_note"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fragrance.id"), index=True)
    note_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("note.id"), index=True)
    note_type: Mapped[NoteType] = mapped_column(SqlEnum(NoteType))
    __table_args__ = (
            UniqueConstraint("fragrance_id", "note_id", name="unique_fragrance_note"),
    )


    fragrance: Mapped["Fragrance"] = relationship(back_populates="notes")
    note: Mapped["Note"] = relationship(back_populates="fragrances")
    
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fragrance.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    rating: Mapped[float] = mapped_column(Float)

    user: Mapped["User"] = relationship(back_populates="reviews")
    fragrance: Mapped["Fragrance"] = relationship(back_populates="fragrance_reviews")
    @validates("rating")
    def validate_rating(self, key, rating):
        if not (1 <= rating <= 10):
            raise ValueError("Rating must be between 1 and 10")
        if (rating * 2) % 1 != 0:  
            raise ValueError("Rating must be a multiple of 0.5 (e.g., 1.0, 1.5, 2.0)")
        return rating
    
    @validates("content")
    def validate_content(self, key, content):
        if not content or len(content.strip()) == 0:
            raise ValueError("Review content cannot be empty")
        if len(content) > 2000:
            raise ValueError("Review content must not exceed 2000 characters")
        return content.strip()


class Wishlist(Base):
    __tablename__ = "user_fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fragrance.id"), index=True)
    status: Mapped[WishListType] = mapped_column(SqlEnum(WishListType), nullable=False, default=WishListType.WANTED)




    user: Mapped["User"] = relationship(back_populates="wishlist")
    fragrance: Mapped["Fragrance"] = relationship(back_populates="users")


class Gender(Enum):
    male = "male"
    mostly_male = "mostly male"
    female = "female"
    mostly_female = "mostly female"
    unisex = "unisex"

class FragranceGender(Base):
    __tablename__ = "fragrance_gender"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender), nullable=False)
    __table_args__ = (
            UniqueConstraint("user_id", "fragrance_id", name="unique_user_fragrance_gender"),
    )


class Season(Enum):
    winter = "winter"
    spring = "spring"
    summer = "summer"
    fall = "fall"

class FragranceSeason(Base):
    __tablename__ = "fragrance_season"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    season: Mapped[Season] = mapped_column(SqlEnum(Season), nullable=False)


class Sillage(Enum):
    intimate = "intimate"
    moderate = "moderate"
    strong = "strong"
    enormous = "enormous"

class FragranceSillage(Base):
    __tablename__ = "fragrance_sillage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    sillage: Mapped[Sillage] = mapped_column(SqlEnum(Sillage), nullable=False)
    __table_args__ = (
            UniqueConstraint("user_id", "fragrance_id", name="unique_user_fragrance_sillage"),
    )

class Longevity(Enum):
    very_weak  = "very weak"
    weak = "weak"
    moderate = "moderate"
    long_lasting = "long lasting"
    eternal = "eternal"

class FragranceLongevity(Base):
    __tablename__ = "fragrance_longevity"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    longevity: Mapped[Longevity] = mapped_column(SqlEnum(Longevity), nullable=False)
    __table_args__ = (
            UniqueConstraint("user_id", "fragrance_id", name="unique_user_fragrance_longevity"),
    )



class PriceValue(Enum):
    way_overpriced = "way overpriced"
    overpriced = "overpriced"
    ok = "ok"
    good_value = "good value"
    great_value = "great value"

class FragrancePriceValue(Base):
    __tablename__ = "fragrance_prive_value"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    price_value: Mapped[PriceValue] = mapped_column(SqlEnum(PriceValue), nullable=False)
    __table_args__ = (
            UniqueConstraint("user_id", "fragrance_id", name="unique_user_fragrance_price_value"),
    )


class FragranceSimilar(Base):
    __tablename__  = "similar_fragrance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    fragrance_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)
    fragrance_that_similar_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("fragrance.id"), index=True)

    __table_args__ = (
        CheckConstraint(
            "fragrance_id != fragrance_that_similar_id",
            name="similar_fragrances_constraint"
        ),
        UniqueConstraint(
            "fragrance_id", "fragrance_that_similar_id",
            name="fragrance_similar_fragrance_constraint"
        ),
    )
