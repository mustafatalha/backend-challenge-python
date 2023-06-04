from typing import Tuple, List, Union

from sqlalchemy.orm import Session

from . import models, schemas


class UnableToBook(Exception):
    pass


class UnableToExtendStay(Exception):
    pass


class BookingNotExist(Exception):
    pass


def create_booking(db: Session, booking: schemas.BookingBase) -> models.Booking:
    (is_possible, reason) = is_booking_possible(db=db, booking=booking)
    if not is_possible:
        raise UnableToBook(reason)
    db_booking = models.Booking(
        guest_name=booking.guest_name, unit_id=booking.unit_id,
        check_in_date=booking.check_in_date, number_of_nights=booking.number_of_nights,
        check_out_date=booking.check_out_date)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def is_booking_possible(db: Session, booking: schemas.BookingBase) -> Tuple[bool, str]:
    # check 1 : The Same guest cannot book the same unit multiple times
    is_same_guest_booking_same_unit = db.query(models.Booking) \
        .filter_by(guest_name=booking.guest_name, unit_id=booking.unit_id).first()

    if is_same_guest_booking_same_unit:
        return False, 'The given guest name cannot book the same unit multiple times'

    # check 2 : the same guest cannot be in multiple units at the same time
    is_same_guest_already_booked = db.query(models.Booking) \
        .filter_by(guest_name=booking.guest_name) \
        .filter(models.Booking.check_out_date > booking.check_in_date,
                booking.check_out_date > models.Booking.check_in_date).first()
    if is_same_guest_already_booked:
        return False, 'The same guest cannot be in multiple units at the same time'

    # check 3 : Unit is available for during stay
    is_unit_available_on_check_in_date = db.query(models.Booking) \
        .filter_by(unit_id=booking.unit_id) \
        .filter(models.Booking.check_out_date > booking.check_in_date,
                booking.check_out_date > models.Booking.check_in_date).first()

    if is_unit_available_on_check_in_date:
        return False, 'For the given check-in date, the unit is already occupied'

    return True, 'OK'


def get_bookings(db: Session, guest_name: str = None, unit_id: str = None) -> Union[models.Booking, List[models.Booking]]:
    """
    Get Booking/s by guest_name and/or unit_id
    """
    # Check if both guest_name and unit_id are given. This condition returns single booking
    if guest_name and unit_id:
        db_booking = db.query(models.Booking).filter_by(guest_name=guest_name, unit_id=unit_id).first()
        if not db_booking:
            raise BookingNotExist(
                f"There is no booking with guest_name={guest_name} and unit_id={unit_id}")
        return db_booking

    # Check if guest_name or unit_id is defined. This condition return a list of bookings
    if guest_name:
        db_bookings: [models.Booking] = db.query(models.Booking).filter_by(guest_name=guest_name).all()
    elif unit_id:
        db_bookings: [models.Booking] = db.query(models.Booking).filter_by(unit_id=unit_id).all()

    if db_bookings:
        return db_bookings

    return []


def create_booking_extension_history(db: Session, extension_hist: schemas.BookingExtensionHistory, booking_id: int = None) -> models.BookingExtensionHistory:
    """
    Create a BookingExtensionHistory record at db from schemas.BookingExtensionHistory
    """
    if booking_id is None:
        # Get the specific user at specific unit_id
        booking = extension_hist.booking
        db_booking: models.Booking = get_bookings(db, guest_name=booking.guest_name, unit_id=booking.unit_id)
        booking_id = db_booking.id

    db_extension = models.BookingExtensionHistory(booking_id=booking_id, extra_nights=extension_hist.extra_nights)
    db.add(db_extension)
    db.commit()
    db.refresh(db_extension)
    return db_extension


def extend_stay(db: Session, guest_name: str, unit_id: str, extra_nights: int) -> models.Booking:
    """
    Extend stay of a customer at a certain unit.
    """
    try:
        # Get the specific user at specific unit_id
        db_booking: models.Booking = get_bookings(db, guest_name=guest_name, unit_id=unit_id)
        new_number_of_nights = db_booking.number_of_nights + extra_nights
        booking = schemas.BookingBase(
            guest_name=db_booking.guest_name,
            unit_id=db_booking.unit_id,
            check_in_date=db_booking.check_in_date,
            number_of_nights=new_number_of_nights
        )
        # Check if extension is possible
        (is_possible, reason) = is_extension_possible(db, booking)
        if not is_possible:
            raise UnableToExtendStay(reason)

        db_booking.number_of_nights = new_number_of_nights
        db_booking.check_out_date = booking.check_out_date

        booking_extension_hist = schemas.BookingExtensionHistory(booking=booking, extra_nights=extra_nights)
        create_booking_extension_history(db, booking_extension_hist, booking_id=db_booking.id)

        return db_booking
    except Exception as e:
        db.rollback()
        raise e


def is_extension_possible(db: Session, booking: schemas.BookingBase) -> Tuple[bool, str]:
    # check 1 : Unit is available for the extension date
    is_unit_available_for_stay = db.query(models.Booking) \
        .filter_by(unit_id=booking.unit_id) \
        .filter(booking.check_out_date > models.Booking.check_in_date, booking.check_in_date < models.Booking.check_in_date )\
        .filter().first()

    if is_unit_available_for_stay:
        return False, 'For the extension period, the unit is already occupied'

    # check 2:  Guest has not another book during the extension date
    is_same_guest_already_booked = db.query(models.Booking) \
        .filter_by(guest_name=booking.guest_name) \
        .filter(models.Booking.check_out_date > booking.check_in_date,
                booking.check_out_date > models.Booking.check_in_date,
                booking.unit_id != models.Booking.unit_id).first()
    if is_same_guest_already_booked:
        return False, 'The same guest cannot be in multiple units at the same time'

    return True, 'OK'
