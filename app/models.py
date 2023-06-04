from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String)
    unit_id = Column(String)
    check_in_date = Column(Date)
    number_of_nights = Column(Integer)
    check_out_date = Column(Date)


class BookingExtensionHistory(Base):
    __tablename__ = "booking_extension_history"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey('booking.id'))
    extra_nights = Column(Integer)
