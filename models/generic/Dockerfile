FROM ubuntu:16.04

MAINTAINER Steven R. Brandt <sbrandt@cct.lsu.edu>

# add build tools and python to the sandbox
# Note: Agave requires openssh-server to be present
RUN apt-get update && \
    apt-get install -y --allow-unauthenticated make build-essential \
                       wget gcc g++ git gfortran git patch flex vim \
                       curl openssh-server python3 python3-pip libz-dev && \
    apt-get purge

ENV CONTAINER_VER ubuntu_16.04
ENV PROCS 10
ENV PATH /usr/local/bin:/usr/bin/:/bin:/usr/sbin:/sbin

#ENV MPICH_VER 3.1.4
COPY mpich.sh /usr/local/bin/mpich.sh
RUN chmod 755 /usr/local/bin/mpich.sh
#RUN mpich.sh

#ENV H5_VER 1.8.21
COPY hdf5.sh /usr/local/bin/hdf5.sh
RUN chmod 755 /usr/local/bin/hdf5.sh
#RUN hdf5.sh

#ENV SWAN_V1 41
ENV SWAN_V2 20
COPY swan.sh /usr/local/bin/swan.sh
RUN chmod 755 /usr/local/bin/swan.sh
#RUN swan.sh

#ENV OPENFOAM_VER 1806
ENV USER root
COPY openfoam.sh /usr/local/bin/openfoam.sh
RUN chmod 755 /usr/local/bin/openfoam.sh
#RUN openfoam.sh
