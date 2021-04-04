FROM python:3.7-slim

WORKDIR /root

COPY ./requirements.txt /root/requirements.txt

ENV PYTHONIOENCODING=utf-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update &&\
    apt-get install -y build-essential curl wget nodejs gnupg

# Install Julia using the Jill installer script to make sure we get the proper version for this platform
ENV PATH="/usr/local/bin:${PATH}"
RUN pip install jill &&\
    jill install 1.5.3 --upstream Official --confirm &&\
    julia -e 'import Pkg; Pkg.add("JSON");'

CMD ["tail", "-f", "/dev/null"]
