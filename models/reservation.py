from datetime import datetime, time
from sqlmodel import Field, SQLModel

from enums.reservation_type import ReservationStatus


class Reservation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_number: str
    space_id: str
    space_name: str
    user_id: str
    user_name: str
    payment_id: int
    r_status: ReservationStatus
    reservation_date: datetime = Field(default_factory=datetime.now)
    use_date: datetime
    start_time: datetime
    end_time: datetime