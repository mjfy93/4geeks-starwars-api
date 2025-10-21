from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Dict, Any, Optional
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), 
        unique=True, 
        nullable=False)
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean(), 
        nullable=False)

    favorites: Mapped[List["Favorites"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active
        }

class Character(db.Model):
    __tablename__="characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50), 
        unique=True,
        nullable=False)
    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=True)
    birth_year: Mapped[str] = mapped_column(
        String(15),
        nullable=True)
    homeplanet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("planets.id"), 
        nullable=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicles.id"), 
        nullable=True)
    homeplanet: Mapped[Optional["Planet"]] = relationship(back_populates="characters")
    vehicle: Mapped[Optional["Vehicle"]] = relationship(back_populates="characters")

    favorites: Mapped[List["Favorites"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan")
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "homeplanet_id": self.homeplanet_id,
            "homeplanet": self.homeplanet.serialize() if self.homeplanet else None,
            "vehicle_id": self.vehicle_id,
            "vehicle": self.vehicle.serialize() if self.vehicle else None
            
        }
    
class Planet(db.Model):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True, 
        nullable=False)
    climate: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True)
    
    characters: Mapped[List["Character"]] = relationship(back_populates="homeplanet")
    favorites: Mapped[List["Favorites"]] = relationship(
        back_populates="planet",
        cascade="all, delete-orphan")
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate
        }

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True, 
        nullable=False)
    model: Mapped[str] = mapped_column(
        String(100),
        unique=True, 
        nullable=True)
    manufacturer: Mapped[str] = mapped_column(
        String(100),
        unique=True, 
        nullable=True)
    
    characters: Mapped[List["Character"]] = relationship(back_populates="vehicle")
    favorites: Mapped[List["Favorites"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan")
    
    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer
        }

class Favorites(db.Model):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False)
    character_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("characters.id"),
        nullable=True)
    planet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("planets.id"),
        nullable=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicles.id"),
        nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())

    
    user: Mapped["User"] = relationship(back_populates="favorites")
    character: Mapped[Optional["Character"]] = relationship(back_populates="favorites")
    planet: Mapped[Optional["Planet"]] = relationship(back_populates="favorites")
    vehicle: Mapped[Optional["Vehicle"]] = relationship(back_populates="favorites")

   
    __table_args__ = (
        UniqueConstraint('user_id', 'character_id', name='unique_user_character'),
        UniqueConstraint('user_id', 'planet_id', name='unique_user_planet'),
        UniqueConstraint('user_id', 'vehicle_id', name='unique_user_vehicle'),
    )

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
            "vehicle_id": self.vehicle_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


