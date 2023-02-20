FROM stevenrbrandt/spack-cmr
USER root
RUN mkdir /spack
RUN chown jovyan /spack
USER jovyan
ENV SPACK_ROOT=/spack
RUN build.sh target=x86_64

RUN perl -p -i -e 's/locks: true/locks: false/' $SPACK_ROOT/etc/spack/defaults/config.yaml
COPY mk-compiler.sh /usr/local/bin/
RUN bash /usr/local/bin/mk-compiler.sh

COPY mk-dflow.sh /usr/local/bin/
RUN bash /usr/local/bin/mk-dflow.sh

## Make sure these builds are available as an upstream
COPY --chown=jovyan upstreams.yaml /home/jovyan/.spack/
COPY --chown=jovyan refresh.sh /home/jovyan/
RUN chmod +x /home/jovyan/refresh.sh
RUN bash /home/jovyan/refresh.sh

USER root
WORKDIR /JSONFiles
COPY cmr-setup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/cmr-setup.sh
COPY --chown=jovyan JSONFiles/* ./
RUN chown jovyan /JSONFiles
RUN date > /etc/build-time.txt
USER jovyan

COPY --chown=jovyan JSONFiles .
RUN /spack/bin/spack find > /JSONFiles/spack-info.txt

WORKDIR /home/jovyan
