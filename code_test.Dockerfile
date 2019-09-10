FROM python:3.7-slim

WORKDIR /root

COPY ./requirements.txt /root/requirements.txt

# TODO: copy in permanent code run stuff?


# TODO remove requirements.txt?

# ENTRYPOINT ["bash"]


CMD ["tail", "-f", "/dev/null"]
