FROM ubuntu:18.04

# Needed to install tzdata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update 
RUN apt-get install -y g++ make python python-pip xauth python3-pip python3 wget git make nodejs npm curl jq sshpass sudo ffmpeg bsdmainutils vim tzdata pkg-config paraview-python
RUN pip3 install --upgrade pip
RUN pip3 install jupyter jupyterhub matplotlib==2.0.2 numpy notebook
RUN pip2 install --upgrade pip
RUN python2 -m pip install ipykernel
RUN npm install -g configurable-http-proxy
RUN apt-get install -y libcairo2-dev libjpeg9-dev

RUN pip3 install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension
RUN pip3 install setvar h5py
WORKDIR /usr/local
RUN git clone https://github.com/TACC/agavepy
RUN cd agavepy && pip install --upgrade --user .
WORKDIR /usr/local
RUN git clone https://github.com/TACC-Cloud/agave-cli cli
#RUN git clone http://github.com/agaveplatform/agave-cli cli
ENV PATH /usr/local/cli/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
RUN touch /etc/bashrc

COPY runuser.sh /usr/local/bin/runuser.sh
RUN chmod +x /usr/local/bin/runuser.sh
RUN useradd -m jovyan -u 1200
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN pip3 install tzupdate
RUN apt-get install -y iproute2 x11-apps net-tools
USER jovyan
ENV HOME /home/jovyan
WORKDIR /home/jovyan

ENV PATH /usr/local/cli/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
CMD /usr/local/bin/runuser.sh
