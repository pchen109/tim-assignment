FROM python:3
LABEL maintainer="psyduck@bcit.ca"

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
RUN mkdir logs
RUN mkdir conf
RUN mkdir data
RUN chown -R nobody:nogroup .
USER nobody

EXPOSE 7777

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]


