FROM python:3.13.2

ENV BASEDIR=/opt/arvi


RUN mkdir -p $BASEDIR/src

COPY  src $BASEDIR/src
COPY requirements.txt $BASEDIR
RUN pip install -r ${BASEDIR}/requirements.txt

WORKDIR $BASEDIR/src

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${API_PORT}"]
