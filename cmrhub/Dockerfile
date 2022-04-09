# It is possible to use a later version of Ubuntu,
# however, if one does that then a Singularity version
# of the image will not run on clusters with older
# linux kernels.
FROM stevenrbrandt/spack-cmr
USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
# python3-pam is needed for authuser.py
RUN apt-get install -y python3 python3-pip openssh-client libssl-dev npm \
  gnupg policycoreutils python3-pam imagemagick curl vim git ffmpeg

# Make python3 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN pip install --upgrade pip

RUN pip install oauthenticator==14.1.0 jupyter==1.0.0 jupyterhub==1.4.2 tornado==6.1 python-oauth2==1.1.1 jupyterhub-dummyauthenticator matplotlib==3.1.2 numpy==1.18.1 ipywidgets==7.5.1 setvar h5py==2.10.0 tzupdate==2.0.0 gui_fun

RUN apt-get -y install nodejs 

RUN npm install -g configurable-http-proxy

# Edit the message in the h1 tags to customize your tutorial
COPY login.html /usr/local/share/jupyterhub/templates/login.html
COPY error.html /usr/local/share/jupyterhub/templates/error.html

# Replace logo.png with whatever logo you wish to use to brand the server
COPY logo.png /usr/local/share/jupyterhub/static/images/logo.png

#RUN mkdir -p /usr/local/lib/python3.5/dist-packages/cyolauthenticator
#COPY cyol.py /usr/local/lib/python3.5/dist-packages/cyolauthenticator/__init__.py
#COPY cyolauthenticator.py /usr/local/lib/python3.5/dist-packages/cyolauthenticator/cyolauthenticator.py
RUN pip install randpass
RUN pip install git+https://github.com/stevenrbrandt/cyolauthenticator

COPY startup.sh /
COPY inituser.sh /
RUN chmod 755 /inituser.sh
COPY jup-config.py /
COPY info.txt /
COPY frame.py /usr/local/bin/
COPY bashrc /etc/skel/.bashrc
COPY bash_profile /etc/skel/.bash_profile
WORKDIR /usr/local/python
RUN git clone -b jetlag2 https://github.com/STEllAR-GROUP/JetLag.git JetLag
RUN mkdir -p /etc/skel/.jupyter/
COPY jupyter_notebook_config.py /etc/skel/.jupyter/
WORKDIR /
RUN git clone --depth 1 -b newmodel https://github.com/ysboss/agave-model.git
CMD bash /startup.sh
