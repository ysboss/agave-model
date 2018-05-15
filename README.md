# agave-model
## Coastal-Modeling Collaborator

To simplify installation, etc., this collaboratory is distributed as a docker container. Please make sure you have docker installed on the laptop or workstation from which you wish to use it.

```
 docker run -it --rm -p 8003:8003 --name model -v /somedirectory/home:/home/jupuser stevenrbrandt/collaboratory
```

Why these arguments?

* -it - That makes the docker session interactive
* --rm - This option will cause docker to clean up after itself when you exit
* -p 8003:8003 - This option tells docker to open port 8003 so you can connect to the notebook
* --name model - It is often helpful to give your docker session a name
* -v /somedirectory/home:/home/jupuser - This will mount the directory /somedirectory/home as the home directory of jupuser inside the container. This docker image will ensure that jupuser has the same userid as you do on the host machine, which means that you can upload files to the container simply by copying them into the /somedirectory/home directory (or one of its subdirectories). Configuration and credentials will also be managed in /somedirectory/home.
* stevenrbrandt/collaboratory - This is the name of the docker image. You can get updates for this image by typing `docker pull stevenrbrandt/collaboratory`
