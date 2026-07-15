from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active
        }


class Person(db.Model):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )
    birth_year: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    height: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    mass: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    hair_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    skin_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    eye_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        back_populates="person"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )
    climate: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )
    terrain: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )
    population: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    diameter: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    rotation_period: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    orbital_period: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    gravity: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        back_populates="planet"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )

    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("person.id"),
        nullable=True
    )

    planet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("planet.id"),
        nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="favorites"
    )

    person: Mapped[Optional["Person"]] = relationship(
        back_populates="favorites"
    )

    planet: Mapped[Optional["Planet"]] = relationship(
        back_populates="favorites"
    )

    def serialize(self):
        if self.person is not None:
            return {
                "id": self.id,
                "type": "person",
                "person_id": self.person_id,
                "name": self.person.name
            }

        if self.planet is not None:
            return {
                "id": self.id,
                "type": "planet",
                "planet_id": self.planet_id,
                "name": self.planet.name
            }

        return {
            "id": self.id,
            "type": "unknown"
        }