FROM archlinux/base
LABEL maintainer="project.ada.lovelace@gmail.com"

RUN pacman --noconfirm -Syy python python-pip nodejs julia gcc
RUN pip install numpy scipy bitstring
RUN pacman --noconfirm -Sy tar && julia -e 'using Pkg; Pkg.add("JSON");'
