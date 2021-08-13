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
WORKDIR /JSONFiles
COPY JSONFiles .
WORKDIR /home/jovyan
