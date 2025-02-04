from sqlalchemy import Column, Integer, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    seats = Column(Integer, nullable=False)
    cost_per_seat = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    num_seats = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    table = relationship("Table")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False)
    reservations = relationship("Reservation")
    # TODO: add expiry date for token
