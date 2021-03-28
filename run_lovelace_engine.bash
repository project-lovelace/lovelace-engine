#!/bin/bash

docker build -t lovelace-engine .
docker run -d -v /var/run/docker.sock:/var/run/docker.sock -p 14714:14714 lovelace-engine
docker ps -a

git clone https://github.com/project-lovelace/lovelace-solutions.git
ln -s lovelace-solutions/python/ solutions

pip install -r requirements.txt

export LOVELACE_SOLUTIONS_DIR=./lovelace-solutions/

