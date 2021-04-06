# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
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

# # Drop schemas
#
# + This notebook is NOT required.
# + Schemas are not typically dropped in a production workflow with real data in it. 
# + At the developmental phase, it might be required for the table redesign.
# + When dropping all schemas is needed, the following is the dependency order.

# Change into the parent directory to find the `dj_local_conf.json` file. 
# When you type `import datajoint as dj` the credentials from `dj_local_conf.json` will be used to log into the database.
import os
os.chdir('..')

from workflow_miniscope.pipeline import *

# +
# imaging.schema.drop()
# scan.schema.drop()
# session.schema.drop()
# subject.schema.drop()
# lab.schema.drop()
# -


