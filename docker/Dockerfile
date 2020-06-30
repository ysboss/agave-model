FROM ubuntu:18.04

# Needed to install tzdata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update 
RUN apt-get install -y g++ make xauth python3-pip python3 wget git make nodejs npm curl \
    jq sshpass sudo ffmpeg bsdmainutils vim tzdata pkg-config paraview-python \
    locales locales-all libcairo2-dev libjpeg9-dev iproute2 x11-apps net-tools
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 2
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2
RUN pip install --upgrade pip
RUN pip install jupyter jupyterhub matplotlib numpy notebook ipywidgets setvar h5py tzupdate gui_fun
RUN npm install -g configurable-http-proxy

RUN jupyter nbextension enable --py widgetsnbextension

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ENV PATH /usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
RUN touch /etc/bashrc
WORKDIR /usr/local/python

COPY runuser.sh /usr/local/bin/runuser.sh
RUN chmod 755 /usr/local/bin/runuser.sh
RUN useradd -m jovyan -u 1200
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN chown jovyan /usr/local/python
USER jovyan
WORKDIR /usr/local/python
RUN git clone https://github.com/STEllAR-GROUP/JetLag.git
ENV HOME /home/jovyan
ENV PYTHONPATH /usr/local/python/JetLag
WORKDIR /home/jovyan

CMD /usr/local/bin/runuser.sh
