FROM python:3.7-slim

WORKDIR /root

COPY ./requirements.txt /root/requirements.txt

# TODO: copy in permanent code run stuff?

ENV PYTHONIOENCODING=utf-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update &&\
  apt-get install -y build-essential &&\
  apt-get install -y nodejs &&\
  apt-get install -y julia &&\
  pip install -r requirements.txt &&\
  rm requirements.txt


# ENTRYPOINT ["bash"]


CMD ["tail", "-f", "/dev/null"]
