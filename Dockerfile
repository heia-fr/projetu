FROM ubuntu:latest
LABEL maintainer="jacques.supcik@hefr.ch"

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required software
RUN apt-get update && apt-get install -y \
  context \
  git \
  python3 \
  python3-pip \
  texlive-latex-extra \
  texlive-latex-recommended \
  texlive-xetex \
  wget \
  wkhtmltopdf

# Install pandoc 2 (Ubuntu only provides pabdoc 1)
WORKDIR /tmp
RUN wget -q https://github.com/jgm/pandoc/releases/download/2.9.2/pandoc-2.9.2-1-amd64.deb
RUN dpkg -i pandoc-2.9.2-1-amd64.deb

# Install fonts
COPY fonts/ /usr/local/share/fonts/
RUN fc-cache -f -v

WORKDIR /app
COPY projetu /app/projetu
COPY setup.py /app
COPY *.yml /app

RUN pip3 install .
