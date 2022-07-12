# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3.8.11 ('ele')
#     language: python
#     name: python3
# ---

# # Configure DataJoint connection to the database
#
# + To run `workflow-miniscope`, we need to properly set up the DataJoint configuration. The configuration will be saved in a file called `dj_local_conf.json` on each machine and this notebook walks you through the process.
#
# + The configuration only needs to be set up once.  If you have gone through the configuration before, directly go to [02-workflow-structure](02-workflow-structure-optional.ipynb).
#
# ## Set up configuration in root directory of this package
#
# + As a convention, we set the configuration up in the root directory of the `workflow-miniscope` package and always start importing DataJoint and pipeline modules from there.

import os
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')

import datajoint as dj

# ## Configure database host address and credentials
#
# Now let's set up the host, user and password in the `dj.config` global variable

import getpass
dj.config['database.host'] = '{YOUR_HOST}'
dj.config['database.user'] = '{YOUR_USERNAME}'
dj.config['database.password'] = getpass.getpass() # enter the password securily

# You should be able to connect to the database at this stage.

dj.conn()

# ## Configure the `custom` field in `dj.config` for element-miniscope
#
# + The major component of the current workflow is the [DataJoint element-miniscope](https://github.com/datajoint/element-miniscope). `element-miniscope` requires configurations in the field `custom` in `dj.config`:
#
# ### Database prefix
#
# + Giving a prefix to schema could help on the configuration of privilege settings. For example, if we set prefix `neuro_`, every schema created with the current workflow will start with `neuro_`, e.g. `neuro_lab`, `neuro_subject`, `neuro_session`, and `neuro_miniscope`.
#
# + The prefix could be configurated as follows in `dj.config`:

dj.config['custom'] = {'database.prefix': 'neuro_'}

# ### Root directories for miniscope calcium imaging raw data and processed results
#
# + `miniscope_root_data_dir` field indicates the root directory for the miniscope raw data from the Miniscope-DAQ acquisition software (e.g. `*.avi`) or the processed results from CaImAn (e.g. `*.hdf5`). The root path typically do not contain information of subjects or sessions, all data from subjects/sessions should be subdirectories in the root path.
#
# + In the database, every path for the raw miniscope data is relative to this root path. The benefit is that the absolute path could be configured for each machine, and when data transfer happens, we just need to change the root directory in the config file.
#
# + The workflow supports multiple root directories. If there are multiple possible root directories, specify the `miniscope_root_data_dir` as a list.
#
# + The root path(s) are specific to each machine, as the name of drive mount could be different for different operating systems or machines.
#
# + In the context of the workflow, all the paths saved into the database or saved in the config file need to be in the POSIX standards (Unix/Linux), with `/`. The path conversion for machines of any operating system is taken care of inside the elements.

# If using our example dataset, downloaded with this notebook [00-data-download](00-data-download-optional.ipynb), the root directory will be:

# If there is only one root path:
dj.config['custom']['miniscope_root_data_dir'] = '/tmp/example_data'
# If there are multiple possible root paths:
dj.config['custom']['miniscope_root_data_dir'] = ['/tmp/example_data']

dj.config

# ## Save the configuration as a json file
#
# With the proper configurations, we could save this as a file, either as a local json file, or a global file.

dj.config.save_local()

# ls

# Local configuration file is saved as `dj_local_conf.json` in the root directory of this package `workflow-miniscope`. Next time if you change your directory to `workflow-miniscope` before importing DataJoint and the pipeline packages, the configurations will get properly loaded.
#
# If saved globally, there will be a hidden configuration file saved in your root directory. The configuration will be loaded no matter where the directory is.

# +
# dj.config.save_global()
# -

# ## Next Step
#
# After the configuration, we will be able to run through the workflow with the [02-workflow-structure](02-workflow-structure-optional.ipynb) notebook.
