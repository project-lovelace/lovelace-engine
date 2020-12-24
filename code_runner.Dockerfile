FROM python:3.7-slim

WORKDIR /root

COPY ./requirements.txt /root/requirements.txt

ENV PYTHONIOENCODING=utf-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update &&\
    apt-get install -y curl &&\
    apt-get install -y build-essential &&\
    apt-get install -y nodejs

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt

ENV PATH="/root/julia/bin:${PATH}"
RUN curl -OJ "https://julialang-s3.julialang.org/bin/linux/x64/1.5/julia-1.5.3-linux-x86_64.tar.gz" &&\
    mkdir julia &&\
    tar xf julia-1.5.3-linux-x86_64.tar.gz -C julia --strip-components 1 &&\
    rm -rf julia-1.5.3-linux-x86_64.tar.gz &&\
    julia -e 'import Pkg; Pkg.add("JSON");'

CMD ["tail", "-f", "/dev/null"]
