FROM mcr.microsoft.com/vscode/devcontainers/anaconda

RUN \
    # dev setup
    apt update && \
    apt-get update && \
    apt-get install sudo git bash-completion graphviz default-mysql-client s3fs procps -y && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade black pip && \
    apt-get clean
COPY ./requirements.txt /tmp/
RUN \
    # workflow dependencies
    # apt-get install gcc ffmpeg libsm6 libxext6 -y && \
    # pip install --no-cache-dir Pygments==2.14.0  && \
    # pip install --no-cache-dir git+https://github.com/flatironinstitute/CaImAn.git  && \
    # git clone https://github.com/flatironinstitute/CaImAn.git  && \
    # pip install --no-cache-dir -r ./CaImAn/requirements.txt  && \
    # pip install --no-cache-dir ./CaImAn && \
    # conda install -c conda-forge caiman -y && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    # clean up
    # rm -rf /tmp/CaImAn && \
    rm /tmp/requirements.txt && \
    apt-get clean

ENV DJ_HOST fakeservices.datajoint.io
ENV DJ_USER root
ENV DJ_PASS simple

ENV MINISCOPE_ROOT_DATA_DIR /workspaces/workflow-miniscope/example_data
ENV DATABASE_PREFIX neuro_

USER vscode
CMD bash -c "sudo rm /var/run/docker.pid; sudo dockerd"