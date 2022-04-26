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
#     language: python
#     name: python3
# ---

# # Interactively run miniscope workflow
#
# + This notebook walks you through the steps in detail to run the `workflow-miniscope`.  
#
# + The workflow requires the data acquired from the UCLA Miniscope and Miniscope-DAQ software and processing with CaImAn.
#
# + If you haven't configured the paths, refer to [01-configure](01-configure.ipynb).
#
# + To overview the schema structures, refer to [02-workflow-structure](02-workflow-structure.ipynb).
#
# + If you need a more automatic approach to run the workflow, refer to [04-automate](04-automate-optional.ipynb).

# Let's change the directory to the package root directory to load the local configuration (`dj_local_conf.json`).

import os
if os.path.basename(os.getcwd())=='notebooks': os.chdir('..')
import numpy as np

# ## `Pipeline.py`
#
# + This script `activates` the DataJoint `Elements` and declares other required tables.

from workflow_miniscope.pipeline import *
from element_interface.utils import find_full_path

# ## Schema diagrams
#
# + The following outputs are the diagrams of the schemas comprising this workflow.
#
# + Please refer back to these diagrams to visualize the relationships of different tables.

dj.Diagram(subject.Subject) + dj.Diagram(session.Session) + \
     dj.Diagram(AnatomicalLocation) + dj.Diagram(Equipment) +  dj.Diagram(miniscope) 

# ## Insert an entry into `subject.Subject`

subject.Subject.heading

subject.Subject.insert1(dict(subject='subject1', 
                             sex='F', 
                             subject_birth_date='2020-01-01', 
                             subject_description='UCLA Miniscope acquisition'))

# ## Insert an entry into `lab.Equipment`

Equipment.insert1(dict(acquisition_hardware='UCLA Miniscope'))

# ## Insert an entry into `session.Session`

session.Session.describe();

session.Session.heading

# +
session_key = dict(subject='subject1', 
                   session_datetime='2021-01-01 00:00:01')

session.Session.insert1(session_key)

session.Session()
# -

# ## Insert an entry into `session.SessionDirectory`
#
# + The `session_dir` is the relative path to the `miniscope_root_data_dir` for the given session, in POSIX format with `/`.
#
# + Instead of a relative path, `session_dir` could be an absolute path but it is not recommended as the absolute path would have to match the `miniscope_root_data_dir` in `dj_local_conf.json`.

session.SessionDirectory.describe();

session.SessionDirectory.heading

# +
session.SessionDirectory.insert1(dict(**session_key, 
                                      session_dir='subject1/session1'))

session.SessionDirectory()
# -

# ## Insert an entry into `miniscope.Recording`

miniscope.Recording.heading

# +
recording_key = dict(**session_key,
                     recording_id=0)

miniscope.Recording.insert1(dict(**recording_key, 
                                 acquisition_hardware='UCLA Miniscope', 
                                 acquisition_software='Miniscope-DAQ-V4',
                                 recording_directory='subject1/session1',
                                 recording_notes='No notes for this session.'))
miniscope.Recording()
# -

# ## Populate `miniscope.RecordingInfo`
#
# + This imported table stores information about the acquired image (e.g. image dimensions, file paths, etc.).
# + `populate` automatically calls `make` for every key for which the auto-populated table is missing data.
# + `populate_settings` passes arguments to the `populate` method.
# + `display_progress=True` reports the progress bar

miniscope.RecordingInfo.describe();

miniscope.RecordingInfo.heading

populate_settings = {'display_progress': True}
miniscope.RecordingInfo.populate(**populate_settings)
miniscope.RecordingInfo()

# ## Insert a new entry into `miniscope.ProcessingParamSet` for CaImAn
#
# + Define and insert the parameters that will be used for the CaImAn processing.
#
# + This step is not needed if you are using an existing ProcessingParamSet.
#
# ### Define CaImAn parameters

avi_files = (miniscope.Recording * miniscope.RecordingInfo * miniscope.RecordingInfo.File & recording_key).fetch('recording_file_path')
avi_files = [find_full_path(get_miniscope_root_data_dir(), 
                         avi_file).as_posix() for avi_file in avi_files]

sampling_rate = (miniscope.Recording * miniscope.RecordingInfo & recording_key).fetch1('fps')

params = dict(fnames=avi_files,
              fr=sampling_rate,
              decay_time=0.4,
              pw_rigid=False,
              max_shifts= (5, 5),
              gSig_filt=(3, 3),
              strides=(48, 48),
              overlaps=(24, 24),
              max_deviation_rigid=3,
              border_nan='copy',
              method_init='corr_pnr',
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
              method_deconvolution='oasis',
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

# ### Insert CaImAn parameters
#
# + A method of the class `ProcessingParamset` called `insert_new_params` is a helper function to insert the CaImAn parameters and ensures that the parameter set inserted is not duplicated.

miniscope.ProcessingParamSet.insert_new_params(
    processing_method='caiman', 
    paramset_id=0, 
    paramset_desc='Calcium imaging analysis with CaImAn using default parameters',
    params=params)

# ## Insert new ProcessingTask to trigger analysis and ingestion of motion correction and segmentation results
#
# + Motion correction and segmentation are performed for each recording in CaImAn.
#
# + If `task_mode=trigger`, this entry will trigger running analysis (i.e. motion correction, segmentation, and traces) within the `miniscope.Processing` table.
#
# + If the `task_mode=load` this step ensures that the output directory contains the valid processed outputs.
#
# + The `paramset_id` is the parameter set stored in `miniscope.ProcessingParamSet` that is used for the imaging processing.
#     
# + The `processing_output_dir` stores the directory of the processing results (relative to the miniscope root data directory).

miniscope.ProcessingTask.insert1(dict(**recording_key,
                                      paramset_id=0,
                                      processing_output_dir='subject1/session1/caiman',
                                      task_mode='trigger'))

# ## Populate `miniscope.Processing`

miniscope.Processing.populate(**populate_settings)

# ## Insert new Curation following the ProcessingTask
#
# + The next step in the pipeline is the curation of motion correction and segmentation results.
#
# + If a manual curation was implemented, an entry needs to be manually inserted into the table `miniscope.Curation`, which specifies the directory to the curated results in `curation_output_dir`. 
#
# + If we would like to use the processed outcome directly, an entry is also needed in `miniscope.Curation`. A method `create1_from_processing_task` was provided to help this insertion. It copies the `processing_output_dir` in `miniscope.ProcessingTask` to the field `curation_output_dir` in the table `miniscope.Curation` with a new `curation_id`.
#
#     + In this example, we create/insert one `miniscope.Curation` for each `miniscope.ProcessingTask`, specifying the same output directory.
#
#     + To this end, we could also make use of a convenient function `miniscope.Curation().create1_from_processing_task()`

miniscope.Curation.insert1(dict(**recording_key,
                              paramset_id=0,
                              curation_id=0,
                              curation_time='2022-04-30 12:22:15', 
                              curation_output_dir='subject1/session1/caiman',
                              manual_curation=False,
                              curation_note=''))

# ## Populate `miniscope.MotionCorrection`
#
# + This table contains the rigid or non-rigid motion correction data including the shifts and summary images.
#

miniscope.MotionCorrection.populate(**populate_settings)

# ## Populate `miniscope.Segmentation`
#
# + This table contains the mask coordinates, weights, and centers.
# + This table also inserts the data into `MaskClassification`, which is the classification of the segmented masks and the confidence of classification.

miniscope.Segmentation.populate(**populate_settings)

# ## Add another set of results from a new round of curation
#
# If you performed curation on an existing processed results (i.e. motion correction or segmentation) then:
#     
# + Add an entry into `miniscope.Curation` with the directory of the curated results and a new `curation_id`.
#
# + Populate the `miniscope.MotionCorrection` and `miniscope.Segmentation` tables again.

# ## Populate `miniscope.Fluorescence`
#
# + This table contains the fluorescence traces prior to filtering and spike extraction.

miniscope.Fluorescence.populate(**populate_settings)

# ## Populate `miniscope.Activity`
# + This table contains the inferred neural activity from the fluorescence traces.

miniscope.Activity.populate(**populate_settings)

# ## Next steps
#
# + Proceed to the [05-explore](05-explore.ipynb) to learn how to  query, fetch, and visualize the imaging data.
