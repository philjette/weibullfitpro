from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create database engine
DATABASE_URL = "sqlite:///weibull_curves.db"
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

class User(Base):
    """Database model for users."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship to curves
    curves = relationship("WeibullCurve", back_populates="user")

class WeibullCurve(Base):
    """Database model for stored Weibull curves."""
    __tablename__ = 'weibull_curves'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    shape = Column(Float, nullable=False)
    scale = Column(Float, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    # Link to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="curves")

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()