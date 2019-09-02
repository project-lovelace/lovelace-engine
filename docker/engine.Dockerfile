FROM python:3.7.4-buster
LABEL maintainer="project.ada.lovelace@gmail.com"

RUN apt-get update && apt-get install -y git lxc

RUN git clone https://github.com/project-lovelace/lovelace-engine.git /engine/
RUN git clone https://github.com/project-lovelace/lovelace-problems.git /problems/

RUN pip install falcon gunicorn numpy scipy

RUN mkdir -p "/var/log/lovelace/" && touch "/var/log/lovelace/lovelace-engine.log"

WORKDIR /engine/
ENV ENGINE_PORT 14714
EXPOSE $ENGINE_PORT
CMD gunicorn --workers 1 --log-level debug --timeout 600 --preload --reload --bind localhost:$ENGINE_PORT engine.api:app
