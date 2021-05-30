FROM python:3.9-alpine3.12
RUN addgroup -S swuser  && adduser -S swuser -G swuser
RUN mkdir /tbot
WORKDIR /tbot
COPY requirements.txt /tbot
RUN pip install -r requirements.txt
COPY . /tbot
USER swuser
CMD [ "python", "./GraciasManel.py" ]