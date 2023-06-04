from typing import List, Union
from http import HTTPStatus

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import UnableToBook, BookingNotExist, UnableToExtendStay
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def hello_world():
    return {"message": "OK"}


@app.post("/api/v1/booking", response_model=schemas.BookingBase)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db=db, booking=booking)
    except UnableToBook as unable_to_book:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=str(unable_to_book))


@app.get("/api/v1/booking", response_model=Union[schemas.BookingBase, List[schemas.BookingBase]])
def get_bookings(guest_name: str = None, unit_id: str = None, db: Session = Depends(get_db)):
    try:
        return crud.get_bookings(db=db, guest_name=guest_name, unit_id=unit_id)
    except BookingNotExist as booking_not_exist:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=str(booking_not_exist))


@app.post("/api/v1/booking/extension", response_model=schemas.BookingBase)
def extend_booking(guest_name: str, unit_id: str, extra_nights: int, db: Session = Depends(get_db)):
    try:
        return crud.extend_stay(db=db, guest_name=guest_name, unit_id=unit_id, extra_nights=extra_nights)
    except UnableToExtendStay as unable_to_extend:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=str(unable_to_extend))
    except BookingNotExist as booking_not_exist:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail=str(booking_not_exist))
