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

The first time you use the Collaboratory, you will need to configure it.

Please use the notebook page:
```
http://localhost:8003/notebooks/UserConfigurator.ipynb
```

You only need to run this web page once. After it is complete, you can run the models by going to the notebook page:
```
http://localhost:8003/notebooks/UserConfigurator.ipynb
http://localhost:8003/notebooks/model.ipynb
```

If you wish to run your code lsu resources, please email sbrandt@cct.lsu.edu and ask for authorization.

If you have questions, please email sbrandt@cct.lsu.edu. Thanks!
