FROM python:3.7.15-alpine3.17

RUN pip install --upgrade pip

WORKDIR /app

ADD . /app

RUN pip install -r musicAI/requirements.txt


CMD [ "python3", "musicAI/musicAI.py" ]

