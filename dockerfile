FROM python:3.13.2

ENV BASEDIR=/opt/arvi


RUN mkdir -p $BASEDIR

COPY  src $BASEDIR

RUN pip install -r requirements.txt

WORKDIR $BASEDIR/src

ENTRYPOINT [ "uvicorn", "main:app", "--reload"]
