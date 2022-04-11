FROM python:3.8.10-alpine

WORKDIR /app
COPY . /app

RUN apk --no-cache update \
 && apk add --no-cache  mariadb-connector-c-dev \
						python3-dev \
						gpgme-dev \
						build-base \
 && pip install -r requirements.txt

ENV FLASK_APP=app_auth
ENV FLASK_DEBUG=1

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80", "--cert=cert.pem", "--key=key.pem"]
EXPOSE 80
