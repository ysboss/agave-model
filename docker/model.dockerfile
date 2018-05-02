FROM ubuntu

RUN apt-get update 
RUN apt-get install -y g++ make python3-pip python3 wget git make nodejs nodejs-legacy npm 
RUN pip3 install --upgrade pip
RUN pip3 install jupyter jupyterhub matplotlib numpy notebook
RUN npm install -g configurable-http-proxy
RUN useradd -m jupuser
USER jupuser
RUN pip3 install ipywidgets
RUN jupyter nbextension enable --py widgetsnbextension
RUN pip3 install setvar --user
WORKDIR /home/jupuser
RUN git clone https://github.com/ysboss/agave-model.git
WORKDIR /home/jupuser/agave-model
CMD jupyter notebook --ip 0.0.0.0 --no-browser --port 8003
