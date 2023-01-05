#! /bin/bash
alias ll='ls -aGg'
export $(grep -v '^#' /main/.env | xargs)

# Install Caiman: WARNING - installation is not often successful on startup.
# Instead, docker exec into the container and environment-minimal.yml command with half
# of dependencies commented out, and then run again for the other half.
cd /main/
git clone --branch master https://github.com/datajoint-company/CaImAn
cd /main/CaImAn
conda install -n base -c conda-forge -y mamba
mamba env update --n base --file environment-minimal.yml
pip install .

cd /main/
echo "INSALL OPTION:" $INSTALL_OPTION

# Always get djarchive
pip install --no-deps git+https://github.com/datajoint/djarchive-client.git

if [ "$INSTALL_OPTION" == "local-all" ]; then # all local installs, mapped from host
    for f in lab animal session event miniscope interface; do
        pip install -e ./element-${f}
    done
    pip install -e ./workflow-miniscope
else  # all except this repo pip installed
    for f in lab animal session event interface; do
         pip install git+https://github.com/${GITHUB_USERNAME}/element-${f}.git
    done
    if [ "$INSTALL_OPTION" == "local-mini" ]; then # only miniscope items from local
        pip install -e ./element-miniscope
        pip install -e ./workflow-miniscope
    elif [ "$INSTALL_OPTION" == "git" ]; then # all from github
        pip install git+https://github.com/${GITHUB_USERNAME}/element-miniscope.git
        pip install git+https://github.com/${GITHUB_USERNAME}/workflow-miniscope.git
    fi
fi

# If test cmd contains pytest, install
if [[ "$TEST_CMD" == *pytest* ]]; then
    pip install pytest
    pip install pytest-cov
    pip install opencv-python
fi
