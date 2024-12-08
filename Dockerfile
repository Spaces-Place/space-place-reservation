FROM python:3.12.3-alpine3.20

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN apk update && apk add python3-dev \
		gcc \
		libc-dev

COPY ./entry_point.sh /code/entry_point.sh
RUN chmod +x /code/entry_point.sh

COPY ./ ./

EXPOSE 80

CMD ["sh", "/code/entry_point.sh"]
