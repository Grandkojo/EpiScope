FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip python3-venv python3
RUN apt-get install nginx -y
RUN apt-get install git -y

COPY . . 

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn


EXPOSE 8000

CMD ["gunicorn", "episcope.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
