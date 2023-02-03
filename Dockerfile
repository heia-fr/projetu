FROM python:3.10-bullseye
ARG TARGETPLATFORM

LABEL maintainer="jacques.supcik@hefr.ch"

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required software
RUN apt-get update && apt-get install -y \
  context \
  git \
  hugo \
  wget

WORKDIR /app
COPY projetu /app/projetu
COPY setup.py /app/
COPY *.yml /app/

RUN pip3 install .
