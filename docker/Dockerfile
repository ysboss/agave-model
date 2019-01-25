FROM ubuntu

# Needed to install tzdata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update 
RUN apt-get install -y g++ make python3-pip python3 wget git make nodejs npm curl jq sshpass sudo ffmpeg bsdmainutils vim tzdata
RUN pip3 install --upgrade pip
RUN pip3 install jupyter jupyterhub matplotlib==2.0.2 numpy notebook
RUN npm install -g configurable-http-proxy

RUN pip3 install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension
RUN pip3 install setvar 
RUN pip3 install h5py
WORKDIR /usr/local
RUN git clone http://github.com/agaveplatform/agave-cli cli

ENV PATH /usr/local/cli/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
RUN touch /etc/bashrc

COPY runuser.sh /usr/local/bin/runuser.sh
RUN chmod +x /usr/local/bin/runuser.sh
RUN useradd -m jovyan -u 1200
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN pip3 install tzupdate
USER jovyan
ENV HOME /home/jovyan
WORKDIR /home/jovyan

ENV PATH /usr/local/cli/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
CMD /usr/local/bin/runuser.sh
