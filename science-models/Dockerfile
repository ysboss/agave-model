FROM ubuntu:xenial
ENV OS_VER ubuntu_xenial

MAINTAINER Steven R. Brandt <sbrandt@cct.lsu.edu>

# add build tools and python to the sandbox
# Note: Agave requires openssh-server to be present
RUN apt-get update && \
    apt-get install -y --allow-unauthenticated make build-essential \
                       wget gcc g++ git gfortran git patch flex vim \
                       curl openssh-server python3 python3-pip && \
    apt-get purge


RUN useradd -m jovyan
RUN mkdir -p /tarballs
RUN chown jovyan /tarballs
RUN mkdir -p /packages/funwave /packages/nhwave /packages/swan

COPY funwave-package.py /packages/funwave/package.py

COPY nhwave-package.py /packages/nhwave/package.py

COPY swan-package.py /packages/swan/package.py
COPY swan-4.1.3.1.tgz /tarballs

COPY spack-init.sh /usr/local/bin
COPY build.sh /usr/local/bin
RUN  chmod +x /usr/local/bin/spack-init.sh /usr/local/bin/build.sh
COPY packages.yaml /usr/local/
RUN mkdir -p /work

USER jovyan
WORKDIR /home/jovyan

ENV SPACK_ROOT=/home/jovyan/spack
ENV PATH ${SPACK_ROOT}/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
