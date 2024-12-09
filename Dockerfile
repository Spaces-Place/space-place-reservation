FROM python:3.12.3-alpine3.20

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp

COPY ./entry_point.sh /code/entry_point.sh
RUN chmod +x /code/entry_point.sh

COPY ./ ./

EXPOSE 80

CMD ["sh", "/code/entry_point.sh"]
