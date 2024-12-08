import json

from sqlmodel import select
from typing import Dict
from fastapi import HTTPException, status, Depends
from enums.reservation_type import ReservationStatus
from models.reservation import Reservation
from utils.mysqldb import get_mysql_session
from utils.kafka_config import KafkaConfig, get_kafka
from utils.logger import Logger


class ReservationService:
    
    def __init__(self, kafka_config: KafkaConfig , logger: Logger):
        self.kafka_config = kafka_config
        self._logger = logger
        self._ready_approval_topic = "reservation.ready.approval"
        self._ready_fail_topic = "reservation.ready.fail"
        self._payment_approval_topic = "reservation.payment.approval"

        # 결제 준비 완료, 결제 실패, 결제 승인
        self.topic_handlers = {
            self._ready_approval_topic: self.ready_approval,
            self._ready_fail_topic: self.ready_fail,
            self._payment_approval_topic: self.start_payment_approval
        }
        self.consumer_groups = {
            self._ready_approval_topic: "reservation_group",
            self._ready_fail_topic: "reservation_group",
            self._payment_approval_topic: "reservation_group"
        }

    async def initialize_consumers(self):
        # 토픽별 컨슈머 초기화
        for topic, group_id in self.consumer_groups.items():
            self.kafka_config.start_consumer(
                topic=topic,
                group_id=group_id,
                message_handler=self.topic_handlers[topic]
            )

        self._logger.info(f"컨슈머 초기화 토픽: {topic}, 그룹: {group_id}")
        
        # 메세지 소비 시작
        await self.kafka_config.start_consuming()


    # sub: 결제 준비 완료
    async def ready_approval(self, message: str):
        print(message)
        try:
            data = json.loads(message)

            async for session in get_mysql_session():
                statement = select(Reservation).filter(Reservation.order_number == data.get("order_number"))
                result = await session.execute(statement)
                payment = result.scalars().first()

                if not payment:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="잘못된 접근입니다.",
                    )
                payment.payment_id = data.get("payment_id")
                await session.commit()
                self._logger.info("결제 번호 저장 완료")

        except Exception as e:
            self._logger.error(f"예약 정보 업데이트 중 오류가 발생했습니다: {e}")

    # sub: 예약 실패 처리
    async def ready_fail(self, message: str):
        print(message)
        try:
            data = json.loads(message)

            async for session in get_mysql_session():
                statement = select(Reservation).filter(Reservation.order_number == data.get("order_number"))
                result = await session.execute(statement)
                reservation = result.scalars().first()

                if not reservation:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="잘못된 접근입니다.",
                    )
                reservation.r_status = ReservationStatus.FAILED
                await session.commit()
                self._logger.info("예약 실패 처리 완료")

        except Exception as e:
            self._logger.error(f"예약 정보 업데이트 중 오류가 발생했습니다: {e}")

    # sub: 예약 성공 처리
    async def start_payment_approval(self, message: str):
        print(message)
        try:
            data = json.loads(message)

            async for session in get_mysql_session():
                statement = select(Reservation).filter(Reservation.order_number == data.get("order_number"))
                result = await session.execute(statement)
                reservation = result.scalars().first()

                if not reservation:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="잘못된 접근입니다.",
                    )
                reservation.r_status = ReservationStatus.COMPLETED
                await session.commit()
                self._logger.info("예약 성공 처리 완료")

        except Exception as e:
            self._logger.error(f"예약 정보 업데이트 중 오류가 발생했습니다: {e}")

async def get_reservation_service(kafka_config: KafkaConfig = Depends(get_kafka), logger: Logger = Depends(Logger.setup_logger)):
    return ReservationService(kafka_config, logger)