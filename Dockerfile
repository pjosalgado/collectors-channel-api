FROM python:3.14.0rc1-slim

LABEL maintainer="Paulo Salgado <pjosalgado@gmail.com>"
LABEL version="1.3.0"

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
