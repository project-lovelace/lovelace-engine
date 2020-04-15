FROM python:3.7
LABEL maintainer="project.ada.lovelace@gmail.com"

WORKDIR /engine/

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /engine/requirements.txt
RUN pip install -r requirements.txt

COPY . /engine/

RUN git clone https://github.com/project-lovelace/lovelace-problems.git /problems/

ENV ENGINE_PORT 14714
EXPOSE $ENGINE_PORT
CMD gunicorn --workers 1 --log-level debug --timeout 600 --preload --reload --bind localhost:$ENGINE_PORT engine.api:app

