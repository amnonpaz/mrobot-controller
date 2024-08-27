FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y -qq \
    pkg-config \
    build-essential \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    libgstreamer1.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gstreamer-1.0 && \
    apt-get autoclean && apt-get autoremove &&  rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install . && mkdir /etc/mrobot-controller/ && cp config/default.json /etc/mrobot-controller/config.json
RUN rm -rf /tmp/app

CMD ["mrobot-controller", "/etc/mrobot-controller/config.json"]
