FROM python:3.7-slim

WORKDIR /root

COPY ./requirements.txt /root/requirements.txt

# TODO: copy in permanent code run stuff?

ENV PYTHONIOENCODING=utf-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'


# TODO remove requirements.txt?

# ENTRYPOINT ["bash"]


CMD ["tail", "-f", "/dev/null"]
