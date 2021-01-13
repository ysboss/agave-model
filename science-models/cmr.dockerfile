FROM stevenrbrandt/spack-cmr
USER root
RUN mkdir /spack
RUN chown jovyan /spack
USER jovyan
ENV SPACK_ROOT=/spack
RUN build.sh
