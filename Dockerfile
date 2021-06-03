##############
# Base Image #
##############

FROM python:3.7.4-slim-buster as base

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    git \
    pciutils \
    graphviz

RUN pip install --upgrade pip \
 && pip install --upgrade setuptools wheel

ADD . /synui
WORKDIR /synui

RUN pip install ./synergos
RUN pip install -r ./requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "./app.py"]