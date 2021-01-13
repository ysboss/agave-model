FROM stevenrbrandt/spack-cmr
USER root
RUN mkdir /spack
RUN chown jovyan /spack
COPY build.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build.sh
USER jovyan
RUN build.sh
