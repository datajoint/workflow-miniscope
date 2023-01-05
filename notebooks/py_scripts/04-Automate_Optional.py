# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3.9.13 ('ele')
#     language: python
#     name: python3
# ---

# %% [markdown] tags=[]
# # DataJoint U24 - Workflow Miniscope
#

# %% [markdown] pycharm={"name": "#%% md\n"}
# ## Workflow Automation
#
# In the previous notebook [03-Process](./03-Process.ipynb), we ran through the workflow in detailed steps, manually adding each. The current notebook provides a more automated approach.
#
# The commands here run a workflow using example data from the [00-DownloadData](./00-DataDownload_Optional.ipynb) notebook, but note where placeholders could be changed for a different dataset.
#

# %% tags=[]
import os
from pathlib import Path

# change to the upper level folder to detect dj_local_conf.json
if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
from workflow_miniscope.pipeline import session, miniscope
from workflow_miniscope import process

# %% [markdown]
# We'll be using the `process.py`'s `run` function automatically loop through all `make` functions, as a shortcut for calling each individually.
#
# If you previously completed the [03-Process notebook](./03-Process.ipynb), you may want to delete the contents ingested there, to avoid duplication errors.
#

# %%
safemode = True  # Set to false to turn off confirmation prompts
(session.Session & 'subject="subject1"').delete(safemode=safemode)
table_list = [
    miniscope.RecordingInfo,
    miniscope.Processing,
    miniscope.MotionCorrection,
    miniscope.Segmentation,
    miniscope.Fluorescence,
    miniscope.Activity,
]
for table in table_list:
    table.delete(safemode=safemode)

# %% [markdown]
# ## Ingestion of subjects, sessions
#
# Refer to the `user_data` folder in the workflow. Fill subject and session information in files `subjects.csv` and `sessions.csv`. We can then use corresponding functions below to automatically ingest subject and session metadata.
#

# %%
from workflow_miniscope.ingest import ingest_subjects, ingest_sessions

ingest_subjects()
ingest_sessions()

# %% [markdown]
# ## Insert new ProcessingParamSet for CaImAn
#
# This is not needed if you are using an existing ProcessingParamSet.
#

# %% jupyter={"outputs_hidden": false} pycharm={"name": "#%%\n"}
params_caiman = dict(
    decay_time=0.4,
    pw_rigid=False,
    max_shifts=(5, 5),
    gSig_filt=(3, 3),
    strides=(48, 48),
    overlaps=(24, 24),
    max_deviation_rigid=3,
    border_nan="copy",
    method_init="corr_pnr",
    K=None,
    gSig=(3, 3),
    gSiz=(13, 13),
    merge_thr=0.7,
    p=1,
    tsub=2,
    ssub=1,
    rf=40,
    stride=20,
    only_init=True,
    nb=0,
    nb_patch=0,
    method_deconvolution="oasis",
    low_rank_background=None,
    update_background_components=True,
    min_corr=0.8,
    min_pnr=10,
    normalize_init=False,
    center_psf=True,
    ssub_B=2,
    ring_size_factor=1.4,
    del_duplicates=True,
    border_pix=0,
    min_SNR=3,
    rval_thr=0.85,
    use_cnn=False,
)

params_dict = dict(
    processing_method="caiman",
    paramset_id=0,  # Change ID if changing parameters
    paramset_desc="Calcium imaging analysis with CaImAn using default parameters",
    params=params_caiman,
)

miniscope.ProcessingParamSet.insert_new_params(**params_dict)

# %% [markdown]
# ## Trigger autoprocessing of the remaining calcium imaging workflow
#

# %% [markdown]
# - The `process.run()` function in the workflow populates every auto-processing table in the workflow. If a table is dependent on a manual table upstream, it will not get populated until the manual table is inserted.
#
# - At this stage, process script populates through the table upstream of `ProcessingTask` (i.e. `RecordingInfo`)
#

# %%
process.run()

# %% [markdown]
# We can then add a processing task as a combination of a scan key, processing parameters, and an output directory.
#

# %%
from element_interface.utils import find_full_path
from workflow_miniscope.pipeline import get_miniscope_root_data_dir

scan_key = (session.Session * miniscope.Recording).fetch("KEY", limit=1)[0]

scan_file = find_full_path(
    get_miniscope_root_data_dir(),
    (miniscope.RecordingInfo.File & scan_key).fetch("file_path", limit=1)[0],
)
caiman_dir = Path(scan_file.parent / "caiman")
miniscope.ProcessingTask.insert1(
    {**scan_key, "paramset_id": 0, "processing_output_dir": caiman_dir}
)

# %% [markdown]
# And trigger the processing

# %%
process.run()

# %% [markdown]
# Next, we would select one of the results at the curation table.

# %%
key = miniscope.Processing.fetch("KEY")[0]
miniscope.Curation.create1_from_processing_task(key)

# %% [markdown]
# And then we can continue processing.

# %%
process.run()

# %% [markdown]
# ## Summary and next step
#
# - This notebook runs through the workflow in an automatic manner.
#
# - The next notebook [05-Explore](./05-Explore.ipynb) discussed the role of each table in more depth.
#
