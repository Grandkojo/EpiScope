FROM ubuntu:20.04
WORKDIR /app

RUN apt update && apt install -y python3-pip python3-venv python3
RUN apt install nginx -y
RUN apt install git -y

COPY . . 
RUN python3 -m venv episcope_env
RUN source episcope_env/bin/activate

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

WORKDIR /app/episcope

EXPOSE 8000

CMD ["gunicorn", "episcope.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
