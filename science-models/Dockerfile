FROM ubuntu:18.04
ENV OS_VER ubuntu_bionicbeaver

MAINTAINER Steven R. Brandt <sbrandt@cct.lsu.edu>

# add build tools and python to the sandbox
# Note: Agave requires openssh-server to be present
RUN apt-get update && \
    apt-get install -y --allow-unauthenticated make build-essential \
                       wget gcc g++ git gfortran git patch flex vim \
                       curl openssh-server python3 python3-pip \
                       ruby uuid-dev pkgconf python3-yaml jq && \
    apt-get purge


RUN useradd -m jovyan
RUN mkdir -p /tarballs
RUN chown jovyan /tarballs

COPY funwave-package.py /packages/funwave/package.py

COPY nhwave-package.py /packages/nhwave/package.py

COPY swan-package.py /packages/swan/package.py
COPY swan-4.1.3.1.tgz /tarballs
COPY swan-4.1.2.1AB.tgz /tarballs

COPY delft3d-package.py /packages/delft3d/package.py
COPY delft3d-6.5.3.tgz /tarballs

COPY spack-init.sh /usr/local/bin
COPY build.sh /usr/local/bin
COPY spack-reconfigure.py /usr/local/bin
COPY singssh /usr/local/bin/
RUN  chmod +x /usr/local/bin/*
COPY packages.yaml /usr/local/
RUN mkdir -p /work
