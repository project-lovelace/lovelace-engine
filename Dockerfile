FROM python:3.7
LABEL maintainer="project.ada.lovelace@gmail.com"

WORKDIR /engine/

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /engine/requirements.txt
RUN pip install -r requirements.txt

COPY . /engine/

RUN ["git", "clone", "https://github.com/project-lovelace/lovelace-problems.git", "/lovelace-problems/"]
RUN ["ln", "-s", "/lovelace-problems/problems/", "problems"]
RUN ["ln", "-s", "/lovelace-problems/resources/", "resources"]

RUN ["git", "clone", "https://$LOVELACE_GITHUB_TOKEN:@github.com/project-lovelace/lovelace-solutions.git", "/lovelace-solutions/"]
RUN ["ln", "-s", "/lovelace-solutions/python/", "solutions"]
RUN ["ln", "-s", "/lovelace-solutions/python/", "/lovelace-problems/problems/solutions"]

EXPOSE 14714

# https://pythonspeed.com/articles/gunicorn-in-docker/
# https://docs.gunicorn.org/en/stable/faq.html#how-do-i-avoid-gunicorn-excessively-blocking-in-os-fchmod
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers", "2", "--log-level", "debug", "--timeout", "600", "--preload", "--reload", "--bind", "0.0.0.0:14714", "engine.api:app"]

