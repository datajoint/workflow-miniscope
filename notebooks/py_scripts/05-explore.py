# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py_scripts//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: 'Python 3.7.9 64-bit (''workflow-calcium-imaging'': conda)'
#     name: python379jvsc74a57bd01a512f474e195e32ad84236879d3bb44800a92b431919ef0b10d543f5012a23c
# ---

# # DataJoint Workflow Miniscope
#
# + This notebook will describe the steps for interacting with the data ingested into `workflow-miniscope`.  

import os
os.chdir('..')

# +
import datajoint as dj
import matplotlib.pyplot as plt
import numpy as np

from workflow_miniscope.pipeline import lab, subject, session, miniscope
# -

# ## Workflow architecture
#
# This workflow is assembled from 4 DataJoint elements:
# + [element-lab](https://github.com/datajoint/element-lab)
# + [element-animal](https://github.com/datajoint/element-animal)
# + [element-session](https://github.com/datajoint/element-session)
# + [element-miniscope](https://github.com/datajoint/element-miniscope)
#
# For the architecture and detailed descriptions for each of those elements, please visit the respective links. 
#
# Below is the diagram describing the core components of the fully assembled pipeline.
#

dj.Diagram(miniscope) + (dj.Diagram(session.Session) + 1) - 1

# ## Browsing the data with DataJoint `query` and `fetch` 
#
# + DataJoint provides functions to query data and fetch.  For detailed tutorials, visit our [general tutorial site](https://codebook.datajoint.io/).
#
# + Running through the pipeline, we have ingested data of subject3 into the database.
#
# + Here are some highlights of the important tables.
#
# ### `Subject` and `Session` tables

subject.Subject()

session.Session()

# + Fetch the primary key for the session of interest which will be used later on in this notebook.

session_key = (session.Session & 'subject = "subject3"' & 'session_datetime = "2021-04-30 12:22:15.032"').fetch1('KEY')

# ### `Recording` and `RecordingInfo` tables
#
# + These tables stores the recording metadata within a particular session.

miniscope.Recording & session_key

miniscope.RecordingInfo & session_key

miniscope.RecordingInfo.Field & session_key

# ### `ProcessingParamSet`, `ProcessingTask`, `Processing`, and `Curation` tables
#
# + The parameters used for CaImAn are stored in `miniscope.ProcessingParamSet` under a `paramset_idx`.
#
# + The processing details for CaImAn are stored in `miniscope.ProcessingTask` and `miniscope.Processing` for the utilized `paramset_idx`.
#
# + After the motion correction and segmentation, the results may go through a curation process. 
#     
#     + If it did not go through curation, a copy of the `miniscope.ProcessingTask` entry is inserted into `miniscope.Curation` with the `curation_output_dir` identical to the `processing_output_dir`.
#
#     + If it did go through a curation, a new entry will be inserted into `miniscope.Curation`, with a `curation_output_dir` specified.
#
#     + `miniscope.Curation` supports multiple curations of an entry in `miniscope.ProcessingTask`.

miniscope.ProcessingParamSet()

miniscope.ProcessingTask * miniscope.Processing & session_key

# In this example workflow, `curation_output_dir` is the same as the `processing_output_dir`, as these results were not manually curated.

miniscope.Curation & session_key

# ### `MotionCorrection` table
#
# + After processing and curation, results are passed to the `miniscope.MotionCorrection` and `miniscope.Segmentation` tables.
#
# + For the example data, the raw data is corrected with rigid and non-rigid motion correction which is stored in `miniscope.MotionCorrection.RigidMotionCorrection` and `miniscope.MotionCorrection.NonRigidMotionCorrection`, respectively. 
#
# + Lets first query the information for one curation.

curation_key = (miniscope.Curation & session_key & 'curation_id=0').fetch1('KEY')

curation_key

miniscope.MotionCorrection.RigidMotionCorrection & curation_key

miniscope.MotionCorrection.NonRigidMotionCorrection & curation_key

# + For non-rigid motion correction, the details for the individual blocks are stored in `imaging.MotionCorrection.Block`.

miniscope.MotionCorrection.Block & curation_key & 'block_id=0'

# + Summary images are stored in `imaging.MotionCorrection.Summary`
#
#     + Reference image - image used as an alignment template
#
#     + Average image - mean of registered frames
#
#     + Correlation image - correlation map (computed during region of interest \[ROI\] detection)
#
#     + Maximum projection image - max of registered frames

miniscope.MotionCorrection.Summary & curation_key & 'field_idx=0'

# + Lets fetch the `average_image` and plot it.

average_image = (miniscope.MotionCorrection.Summary & curation_key & 'field_idx=0').fetch1('average_image')

plt.imshow(average_image);

# ### `Segmentation` table
#
# + Lets fetch and plot a mask stored in the `miniscope.Segmentation.Mask` table for one `curation_id`.
#
# + Each mask can be associated with a field by the attribute `mask_center_z`.  For example, masks with `mask_center_z=0` are in the field identified with `field_idx=0` in `miniscope.RecordingInfo`.

mask_xpix, mask_ypix = (miniscope.Segmentation.Mask * miniscope.MaskClassification.MaskType & curation_key & 'mask_center_z=0' & 'mask_npix > 130').fetch('mask_xpix','mask_ypix')

mask_image = np.zeros(np.shape(average_image), dtype=bool)
for xpix, ypix in zip(mask_xpix, mask_ypix):
    mask_image[ypix, xpix] = True

plt.imshow(average_image);
plt.contour(mask_image, colors='white', linewidths=0.5);

# ### `MaskClassification` table
#
# + This table provides the `mask_type` and `confidence` for the mask classification.

miniscope.MaskClassification.MaskType & curation_key & 'mask=0'

# ### `Fluorescence` and `Activity` tables
#
# + Lets fetch and plot the flourescence and activity traces for one mask.

query_cells = (miniscope.Segmentation.Mask * miniscope.MaskClassification.MaskType & curation_key & 'mask_center_z=0' & 'mask_npix > 130').proj()

# +
fluorescence_traces = (miniscope.Fluorescence.Trace & query_cells).fetch('fluorescence', order_by='mask')

activity_traces = (miniscope.Activity.Trace & query_cells).fetch('activity_trace', order_by='mask')

sampling_rate = (miniscope.RecordingInfo & curation_key).fetch1('fps') # [Hz]

# +
fig, ax = plt.subplots(1, 1, figsize=(16, 4))
ax2 = ax.twinx()

for f, a in zip(fluorescence_traces, activity_traces):
    ax.plot(np.r_[:f.size] * 1/sampling_rate, f, 'k', label='fluorescence trace')    
    ax2.plot(np.r_[:a.size] * 1/sampling_rate, a, 'r', alpha=0.5, label='deconvolved trace')
    
    break

ax.tick_params(labelsize=14)
ax2.tick_params(labelsize=14)

ax.legend(loc='upper left', prop={'size': 14})
ax2.legend(loc='upper right', prop={'size': 14})

ax.set_xlabel('Time (s)')
ax.set_ylabel('Activity (a.u.)')
ax2.set_ylabel('Activity (a.u.)');
# -

# ## Summary and Next Step
#
# + This notebook highlights the major tables in the workflow and visualize some of the ingested results. 
#
# + The next notebook [06-drop](06-drop-optional.ipynb) shows how to drop schemas and tables if needed.
