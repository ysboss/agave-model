FROM ubuntu

RUN apt-get update 
RUN apt-get install -y g++ make python3-pip python3 wget git make nodejs npm curl jq sshpass sudo ffmpeg bsdmainutils vim
RUN pip3 install --upgrade pip
RUN pip3 install jupyter jupyterhub matplotlib==2.0.2 numpy notebook
RUN npm install -g configurable-http-proxy

RUN pip3 install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension
RUN pip3 install setvar 
WORKDIR /usr/local
RUN git clone http://github.com/agaveplatform/agave-cli cli

RUN echo 'export PATH=/usr/local/cli/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin' > /etc/bashrc

WORKDIR /

COPY mkuser.sh mkuser.sh
COPY runuser.sh runuser.sh
RUN chmod +x runuser.sh

CMD bash mkuser.sh
