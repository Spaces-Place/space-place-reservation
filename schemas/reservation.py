
from pydantic import BaseModel, Field


class ReservationRequest(BaseModel):
    space_id: str = Field(description="공간 고유번호")
    space_name: str = Field(description="공간 이름")
    user_name: str = Field(description="예약자 이름")
    use_date: str = Field(default='', description="이용일(YYYY-MM-DD)")
    start_time: str = Field(default='', description="이용 시작 시간")
    end_time: str = Field(default='', description="이용 종료 시간")    

class UpdatePaymentIdRequest(BaseModel):
    payment_id: int = Field(description="결제 고유번호")
    order_number: str = Field(description="주문번호")

class OrderNumberRequest(BaseModel):
    order_number: str = Field(description="주문번호")