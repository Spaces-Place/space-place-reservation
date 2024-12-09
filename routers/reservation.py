from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from enums.reservation_type import ReservationStatus
from models.reservation import Reservation
from schemas.reservation import (
    ReservationRequest,
    OrderNumberRequest,
    UpdatePaymentIdRequest,
)
from utils.authenticate import userAuthenticate
from utils.mysqldb import get_mysql_session


reservation_router = APIRouter(tags=["예약"])


@reservation_router.get(
    "", response_model=Dict, status_code=status.HTTP_200_OK, summary="예약 목록 확인"
)
async def get_reservations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    session=Depends(get_mysql_session),
    token_info=Depends(userAuthenticate),
):
    statement = (
        select(Reservation)
        .where(Reservation.user_id == token_info["user_id"])
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(statement)
    reservations = result.scalars().all()

    return {"reservations": reservations}


@reservation_router.post(
    "/kakao/ready",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="예약 결제 준비",
)
async def get_order_number(
    data: ReservationRequest,
    session=Depends(get_mysql_session),
    token_info=Depends(userAuthenticate),
):
    """구현이 필요하지 않습니다."""
    now = datetime.now()
    order_prefix = now.strftime("%Y%m%d%H%M%S")

    # 전날~오늘 검색 조건 추가 시 성능 향상 기대
    statement = (
        select(Reservation)
        .where(Reservation.order_number.like(f"{order_prefix}%"))
        .order_by(Reservation.order_number.desc())
    )
    result = await session.execute(statement)
    last_order = result.scalar()

    if last_order:
        last_order_number = int(last_order.order_number[-4:])
        order_number = f"{order_prefix}{last_order_number + 1:04d}"
    else:
        order_number = f"{order_prefix}0000"

    reservation_data = {
        "order_number": order_number,
        "space_id": data.space_id,
        "space_name": data.space_name,
        "user_id": token_info["user_id"],
        "user_name": data.user_name,
        "r_status": ReservationStatus.PENDING,
        "reservation_date": now
    }

    if data.use_date:
        reservation_data["use_date"] = data.use_date
    else:
        reservation_data["start_time"] = data.start_time
        reservation_data["end_time"] = data.end_time

    new_reservation = Reservation(**reservation_data)

    session.add(new_reservation)
    await session.commit()
    return {"order_number": order_number}


# payment_id 업데이트
@reservation_router.patch(
    "/kakao/ready",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="결제 준비 번호 업데이트",
)
async def update_payment_id(
    update_request: UpdatePaymentIdRequest,
    session=Depends(get_mysql_session),
    token_info=Depends(userAuthenticate),
):
    """구현이 필요하지 않습니다."""
    # 전날~오늘 검색 조건 추가 시 성능 향상 기대
    statement = select(Reservation).filter(
        Reservation.order_number == update_request.order_number
    )
    result = await session.execute(statement)
    reservation = result.scalars().first()
    if reservation:
        reservation.payment_id = update_request.payment_id
        await session.commit()
        await session.refresh(reservation)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 주문번호가 존재하지 않습니다.",
        )


# r_status = COMPLETED
@reservation_router.patch(
    "/kakao/approve", status_code=status.HTTP_204_NO_CONTENT, summary="예약 완료 처리"
)
async def update_payment_id(
    approve_request: OrderNumberRequest,
    token_info=Depends(userAuthenticate),
    session=Depends(get_mysql_session),
):
    """구현이 필요하지 않습니다."""
    # 전날~오늘 검색 조건 추가 시 성능 향상 기대
    statement = select(Reservation).filter(
        Reservation.order_number == approve_request.order_number
    )
    result = await session.execute(statement)
    reservation = result.scalars().first()
    if reservation:
        reservation.r_status = ReservationStatus.COMPLETED
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 주문번호가 존재하지 않습니다.",
        )


# r_status = FAILED
@reservation_router.patch(
    "/kakao/fail", status_code=status.HTTP_204_NO_CONTENT, summary="예약 실패 처리"
)
async def update_payment_id(
    fail_request: OrderNumberRequest,
    token_info=Depends(userAuthenticate),
    session=Depends(get_mysql_session),
):
    """구현이 필요하지 않습니다."""
    # 전날~오늘 검색 조건 추가 시 성능 향상 기대
    statement = select(Reservation).filter(
        Reservation.order_number == fail_request.order_number
    )
    result = await session.execute(statement)
    reservation = result.scalars().first()
    if reservation:
        reservation.r_status = ReservationStatus.FAILED
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 주문번호가 존재하지 않습니다.",
        )


# r_status = CANCELED
@reservation_router.patch(
    "/kakao/cancel", status_code=status.HTTP_204_NO_CONTENT, summary="예약 취소 처리"
)
async def update_payment_id(
    cancel_request: OrderNumberRequest,
    token_info=Depends(userAuthenticate),
    session=Depends(get_mysql_session),
):
    """구현이 필요하지 않습니다."""
    # 전날~오늘 검색 조건 추가 시 성능 향상 기대
    statement = select(Reservation).filter(
        Reservation.order_number == cancel_request.order_number
    )
    result = await session.execute(statement)
    reservation = result.scalars().first()
    if reservation:
        reservation.r_status = ReservationStatus.CANCELED
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일치하는 주문번호가 존재하지 않습니다.",
        )
