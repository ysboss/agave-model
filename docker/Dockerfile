#FROM ubuntu:18.04
FROM stevenrbrandt/spack-cmr
USER root

# Needed to install tzdata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update 
RUN apt-get install -y g++ make xauth python3-pip python3 wget git make nodejs npm curl \
    jq sshpass sudo ffmpeg bsdmainutils vim tzdata pkg-config \
    locales locales-all libcairo2-dev libjpeg9-dev iproute2 x11-apps net-tools
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 2
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2
RUN pip3 install --upgrade pip==19.3.1
RUN pip3 install jupyter jupyterhub==1.0.0 matplotlib==3.1.2 numpy==1.18.1 notebook==6.0.2 ipywidgets==7.5.1 setvar h5py==2.10.0 tzupdate==2.0.0 gui_fun
#RUN npm install -g npm
RUN npm install -g configurable-http-proxy@4.2.0
#RUN pip install --upgrade pip
#RUN pip install jupyter jupyterhub matplotlib numpy notebook ipywidgets setvar h5py tzupdate gui_fun
#RUN npm install -g npm@5.3.0
#RUN npm install -g configurable-http-proxy

RUN jupyter nbextension enable --py widgetsnbextension

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

ENV PATH /usr/local/bin:/usr/bin:/bin:/usr/sbin:/usr/local/sbin:/sbin
RUN touch /etc/bashrc
WORKDIR /usr/local/python

COPY runuser.sh /usr/local/bin/runuser.sh
RUN chmod 755 /usr/local/bin/runuser.sh
# RUN useradd -m jovyan -u 1200
RUN echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN chown jovyan /usr/local/python
RUN find /home/jovyan | xargs chown jovyan
RUN usermod jovyan --shell /bin/bash
WORKDIR /
RUN git clone -b newmodel https://github.com/ysboss/agave-model.git
RUN find agave-model | xargs -d '\n' chown jovyan
USER jovyan
WORKDIR /usr/local/python
RUN git clone -b jetlag2 https://github.com/STEllAR-GROUP/JetLag.git JetLag
ENV PYTHONPATH /usr/local/python/JetLag
RUN mkdir -p /home/jovyan/notebooks
WORKDIR /home/jovyan/notebooks
RUN cp /agave-model/model.ipynb /agave-model/vis*.ipynb .

CMD /usr/local/bin/runuser.sh
