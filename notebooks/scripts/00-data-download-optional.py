# ---
# jupyter:
#   jupytext:
#     formats: ipynb,scripts//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: 'Python 3.7.9 64-bit (''workflow-calcium-imaging'': conda)'
#     name: python379jvsc74a57bd01a512f474e195e32ad84236879d3bb44800a92b431919ef0b10d543f5012a23c
# ---

# # Download example dataset
#
# + This workflow will need miniscope calcium imaging data collected from the UCLA Miniscope and processed with CaImAn.  We provide an example dataset to be downloaded to run through the workflow. This notebook walks you through the process to download the dataset.
#
# ## Install `djarchive-client`
#
# + The example dataset is hosted on `djarchive`, an AWS storage.
#
# + We provide a client package, [djarchive-client](https://github.com/datajoint/djarchive-client), to download the data which can be installed with pip:

pip install git+https://github.com/datajoint/djarchive-client.git

# ## Download example datasets using `djarchive-client`

import djarchive_client
client = djarchive_client.client()

# Browse the datasets that are available on `djarchive`:

list(client.datasets())

# Browse the different versions of each dataset:

list(client.revisions())

# To download the dataset, let's prepare a directory, for example in `/tmp`:

import os
os.mkdir('/tmp/example_data')

# Run download for a given dataset and revision:

client.download('workflow-miniscope-test-set', target_directory='/tmp/example_data', revision='v1')

# ## Directory structure
#
# + After downloading, the directory will be organized as follows:
#
#     ```
#     /tmp/example_data/
#     - subject1/
#         - session1/
#             - 0.avi
#             - metaData.json
#             - timeStamps.csv
#             - caiman/
#                 - subject1_session1.hdf5
#     ```
#
# + subject 1 data is recorded with the UCLA Miniscope and Miniscope-DAQ-V4 acquisition software, and processed with CaImAn.
#
# + We will use the dataset for subject 1 as an example for the rest of the notebooks. If you use your own dataset for the workflow, change the path accordingly.
#
# ## Next step
#
# + In the next notebook ([01-configure](01-configure.ipynb)) we will set up the configuration file for the workflow.

#
