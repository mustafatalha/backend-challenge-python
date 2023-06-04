import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
    guest_name: str
    unit_id: str
    check_in_date: datetime.date
    number_of_nights: int

    @property
    def check_out_date(self) -> datetime.date:
        """ Computed field check out date"""
        return self.check_in_date + datetime.timedelta(days=self.number_of_nights)

    class Config:
        orm_mode = True


class BookingExtensionHistory(BaseModel):
    booking: BookingBase
    extra_nights: int

    class Config:
        orm_mode = True
