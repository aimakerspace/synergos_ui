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

RUN pip install ./synergos

ADD ./synui_view /src
WORKDIR /src
RUN pip install -r ./synui_view/requirements.txt

RUN ls /src

EXPOSE 3000

ENTRYPOINT ["streamlit", "run", "--server.port", "3000", "./app.py"]