FROM python:3.9-slim

LABEL MAINTAINER="Paulo Salgado <pjosalgado@gmail.com>"
LABEL VERSION="$VERSION"

WORKDIR /python-docker

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
