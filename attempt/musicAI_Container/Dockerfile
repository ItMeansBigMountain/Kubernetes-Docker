FROM python:3.7.15-alpine3.17

RUN pip install --upgrade pip

# Current directory
WORKDIR /app

# copy all from current directory --> /app directory inside container
ADD . /app

# run command in current dir
RUN pip install -r musicAI/requirements.txt

# open ports
EXPOSE 80
EXPOSE 8080

CMD [ "python3", "musicAI/musicAI.py" ]

