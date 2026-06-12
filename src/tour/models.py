from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from src.db.database import Base

class Lands(Base):
    __tablename__ = "lands"

    id:Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    cities: Mapped[list["City"]] = relationship(back_populates="land", cascade="all, delete-orphan")

    landmarks: AssociationProxy[list["Landmarks"]] = association_proxy("cities", "landmarks")

    favorite = relationship("FavoriteLands", back_populates="land")


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    land_id: Mapped[int] = mapped_column(ForeignKey("lands.id"))

    land: Mapped["Lands"] = relationship(back_populates="cities")

    landmarks: Mapped[list["Landmarks"]] = relationship(back_populates="city", cascade="all, delete-orphan")

    favorite = relationship("FavoriteCity", back_populates="city")


class Landmarks(Base): 
    __tablename__ = "landmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    address: Mapped[str]
    description: Mapped[str] 

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))

    city: Mapped["City"] = relationship(back_populates="landmarks")

    favorite = relationship("FavoriteLandmarks", back_populates="landmark")


class FavoriteLands(Base):
    __tablename__ = "favorite_lands"

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), primary_key=True)

    land: Mapped["Lands"] = relationship(back_populates="favorite")


class FavoriteCity(Base):
    __tablename__ = "favorite_cities"

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'), primary_key=True)

    city: Mapped["City"] = relationship(back_populates="favorite")


class FavoriteLandmarks(Base):
    __tablename__ = "favorite_landmarks"

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    landmark_id: Mapped[int] = mapped_column(ForeignKey('landmarks.id'), primary_key=True)

    landmark: Mapped["Landmarks"] = relationship(back_populates="favorite")