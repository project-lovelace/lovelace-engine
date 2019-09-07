FROM python:3.7-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# TODO: copy in permanent code run stuff?

RUN pip install -r requirements.txt

# TODO remove requirements.txt?

ENTRYPOINT ["bash"]


# CMD ["src/run.py"]
