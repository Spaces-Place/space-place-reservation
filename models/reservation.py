from datetime import datetime, time
from sqlmodel import Field, SQLModel

from enums.reservation_type import ReservationStatus


class Reservation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_number: str
    space_id: str
    user_id: str
    payment_id: int
    r_status: ReservationStatus
    reservation_date: datetime = Field(default_factory=datetime.now)
    use_date: datetime
    start_time: time
    end_time: time