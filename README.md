# Coastal Model Repository (CMR)

## Installation and startup

To simplify installation, etc., this collaboratory is distributed as a docker container. Please make sure you have docker and docker-compose installed on the laptop or workstation from which you wish to use it.

To start up the CMR, issue the following commands:

```
git clone https://github.com/ysboss/agave-model.git
cd agave-model/docker
docker-compose up
```

When the container starts up, you will be shown an URL which you can copy into your local browser to access the notebook.

Because the container names the image `cmr` you can use docker commands like the following to move data
into and out of the image:

```
docker cp input.tgz cmr:/home/jovyan/agave-model/
docker cp cmr:/home/jovyan/agave-model/output.tgz .
```

## Using the Collaboratory

The first time you use the Collaboratory, you will need to configure it. To do this, click on the `configuration2.ipynb` notebook and execute the first cell. You will then be prompted to provide your Agave password and username. You can get this credential from here: http://togo.agaveplatform.org/auth/#/login

Once you fill in this information, your screen should look similar to this:

<img src='images/Config.png'>

The other parameters for running jobs through the collaboratory have been prepopulated with those needed to run on LSU resources. If you wish to use those resources, please email sbrandt@cct.lsu.edu and ask for authorization.
