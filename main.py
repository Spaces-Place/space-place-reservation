import asyncio
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from routers.reservation import reservation_router
from utils.database_config import DatabaseConfig
from utils.logger import Logger
from utils.kafka_config import get_kafka
from services.reservation_service import ReservationService


async def start_payment_consumers():
    kafka_config = get_kafka()
    logger = Logger.setup_logger()
    payment_service = ReservationService(kafka_config, logger)
    await payment_service.initialize_consumers()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작될 때 실행할 코드"""

    env_type = (
        ".env.development"
        if os.getenv("APP_ENV") == "development"
        else ".env.production"
    )
    load_dotenv(env_type)

    database = DatabaseConfig().create_database()
    await database.initialize()

    consumer_task = asyncio.create_task(start_payment_consumers())

    yield

    """애플리케이션 종료될 때 실행할 코드 (필요 시 추가)"""
    consumer_task.cancel()
    await asyncio.gather(consumer_task, return_exceptions=True)
    await database.close()


app = FastAPI(lifespan=lifespan, title="예약 API", version="ver.1")

app.include_router(reservation_router, prefix="/api/v1/reservations")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(logger: Logger = Depends(Logger.setup_logger)) -> dict:
    logger.info("health check")
    return {"status": "ok"}


"""Trace"""
# OpenTelemetry
resource = Resource.create({ResourceAttributes.SERVICE_NAME: "reservation-service"})
trace_provider = TracerProvider(resource=resource)

# 템포에 데이터 전송을 위한 OLTP span Exporter
tempo_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
span_processor = BatchSpanProcessor(tempo_exporter)
trace_provider.add_span_processor(span_processor)  # Span 프로세서 추가

trace.set_tracer_provider(trace_provider)

FastAPIInstrumentor.instrument_app(app, excluded_urls="client/.*/health")
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)  # 메트릭(/metrics) 노출


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용하는 URL 넣어야함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
