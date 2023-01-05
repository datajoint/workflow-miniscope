FROM datajoint/djbase:py3.9-debian-8eb1715

USER anaconda:anaconda

COPY ./workflow-miniscope/docker/apt_requirements.txt /tmp/
RUN /entrypoint.sh echo "Installed dependencies."

WORKDIR /main/workflow-miniscope

# Always move local - conditional install in setup.sh
COPY --chown=anaconda:anaconda ./element-lab/ /main/element-lab/
COPY --chown=anaconda:anaconda ./element-animal/ /main/element-animal/
COPY --chown=anaconda:anaconda ./element-session/ /main/element-session/
COPY --chown=anaconda:anaconda ./element-event/ /main/element-event/
COPY --chown=anaconda:anaconda ./element-interface/ /main/element-interface/
COPY --chown=anaconda:anaconda ./element-miniscope/ /main/element-miniscope/
COPY --chown=anaconda:anaconda ./workflow-miniscope/ /main/workflow-miniscope/

# Conditional install - local-all, local-dlc, or git
COPY --chown=anaconda:anaconda ./workflow-miniscope/docker/setup.sh /main/
COPY --chown=anaconda:anaconda ./workflow-miniscope/docker/.env /main/
RUN chmod 755 /main/setup.sh
RUN chmod 755 /main/.env
RUN /main/setup.sh
RUN rm -f ./dj_local_conf.json

# Install Caiman
RUN git clone --branch master https://github.com/datajoint-company/CaImAn
WORKDIR /main/CaImAn
RUN conda install -n base -c conda-forge -y mamba
RUN /bin/bash -c 'mamba env update --n base --file environment.yml'
RUN pip install .
