from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
Base = declarative_base()
class Organizer(Base):
    __tablename__ = 'organizers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    verified = Column(Boolean, default=False)
class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String); city = Column(String); state = Column(String); postal_code = Column(String)
    lat = Column(Float); lng = Column(Float)
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime)
    timezone = Column(String); format = Column(String)
    audience = Column(ARRAY(String)); language = Column(String)
    cost_min = Column(Float); cost_max = Column(Float); badges = Column(ARRAY(String))
    organizer_id = Column(Integer, ForeignKey('organizers.id'))
    venue_id = Column(Integer, ForeignKey('venues.id'))
    source = Column(String); source_id = Column(String); verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    organizer = relationship('Organizer')
    venue = relationship('Venue')
