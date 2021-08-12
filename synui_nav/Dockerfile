##############
# Base Image #
##############

FROM python:3.7.4-slim-buster as base

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential git

RUN pip install --upgrade pip \
 && pip install --upgrade setuptools wheel

ADD . /src
WORKDIR /src

RUN pip install -r ./requirements.txt

EXPOSE 4000

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4000"]
