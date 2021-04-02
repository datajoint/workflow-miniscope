# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: 'Python 3.7.10 64-bit (''workflow-miniscope'': conda)'
#     metadata:
#       interpreter:
#         hash: fb69438121b2de1073146525f02c3c959a56b9d2c1d6b0a62c34f01201323d1c
#     name: python3
# ---

# # Insert an entry into `imaging.ProcessingParamSet`
#
# + The entry will comprise the parameters used for processing with the analysis package.
#
# + If the same parameters are used to analyze multiple datasets, the parameters only need to be inserted once.
#
# + This step is in a separate Jupyter Notebook because the parameters would otherwise clutter the next main notebook (`01ingest.ipynb`).

# Change into the parent directory to find the `dj_local_conf.json` file. 
# When you type `import datajoint as dj` the credentials from `dj_local_conf.json` will be used to log into the database.
import os
os.chdir('..')

import numpy as np
from workflow_miniscope.pipeline import *

# ## Define the `MiniscopeAnalysis` parameters

params = dict(pars_envs = ['memory_size_to_use', 12, 'memory_size_per_patch', 0.6, 'patch_dims', [64, 64]],
              include_residual = False,
              gSig = 3,           
              gSiz = 15,
              ssub = 1,
              with_dendrites = True,
              updateA_search_method = 'dilate',
              updateA_bSiz = 5,
              updateA_dist = None,
              spatial_constraints = ['connected', True, 'circular', False],
              spatial_algorithm = 'hals_thresh',
              Fs = 30,
              tsub = 5,
              deconv_flag = True,
              deconv_options = ['type', 'ar1', 'method', 'constrained', 'smin', -5, 'optimize_pars', True, 'optimize_b', True, 'max_tau', 100],
              nk = 3,
              detrend_method = 'spline',
              bg_model = 'ring',
              nb = 1,
              ring_radius = 23,
              num_neighbors = [],
              show_merge = False,
              merge_thr = 0.65,
              method_dist = 'max',
              dmin = 5,
              dmin_only = 2,
              merge_thr_spatial = [0.8, 0.4, -float('inf')],
              K = [],
              min_corr = 0.9,
              min_pnr = 15,
              min_pixel = None,
              bd = 0,
              frame_range = [],
              save_initialization = False,
              use_parallel = True,
              show_init = False,
              choose_params = False,
              center_psf = True,
              min_corr_res = 0.7,
              min_pnr_res = 8,
              seed_method_res = 'auto',
              update_sn = True,
              with_manual_intervention = False)

# ## Insert the `MiniscopeAnalysis` parameters
#
# + The `insert_new_params` is a utility function as part of the `imaging.ProcessingParamSet` table that is used to verify the parameter set does not already exist in the table.

imaging.ProcessingParamSet.insert_new_params(
                            processing_method='mcgill_miniscope_analysis', 
                            paramset_idx=0, 
                            paramset_desc='Calcium imaging analysis with Miniscope Analysis using default parameters', 
                            params=params)

# ## Proceed to the `01ingest.ipynb` Jupyter Notebook
#
# + This notebook describes the steps to ingest the imaging metadata and processed data.
