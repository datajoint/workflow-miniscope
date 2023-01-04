#! /bin/bash
alias ll='ls -aGg'
export $(grep -v '^#' /main/.env | xargs)

echo "INSALL OPTION:" $INSTALL_OPTION
cd /main/

# Always get djarchive
echo "----------- DJARCHIVE HERE --------------"
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
    echo "----------- CAIMAN HERE --------------" # Install Caiman
    wget 'https://raw.githubusercontent.com/datajoint-company/CaImAn/master/environment-minimal.yml' -O /tmp/CaImAn_env.yml
    conda install -n base -c conda-forge -y mamba
    mamba env update --n base --file /tmp/CaImAn_env.yml
    cd /main/
fi
