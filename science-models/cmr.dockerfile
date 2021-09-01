FROM stevenrbrandt/spack-cmr
USER root
RUN mkdir /spack
RUN chown jovyan /spack
USER jovyan
ENV SPACK_ROOT=/spack
RUN build.sh target=x86_64

# Make sure these builds are available as an upstream
COPY --chown=jovyan upstreams.yaml /home/jovyan/.spack/
COPY --chown=jovyan refresh.sh /home/jovyan/
RUN chmod +x /home/jovyan/refresh.sh
RUN bash /home/jovyan/refresh.sh

USER root
WORKDIR /JSONFiles
RUN chown jovyan /JSONFiles
USER jovyan

COPY --chown=jovyan JSONFiles .
RUN /spack/bin/spack find > /JSONFiles/spack-info.txt

WORKDIR /home/jovyan
