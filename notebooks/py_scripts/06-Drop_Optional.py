# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: ele
#     language: python
#     name: python3
# ---

# # Drop schemas
#
# + Schemas are not typically dropped in a production workflow with real data in it. 
# + At the developmental phase, it might be required for the table redesign.
# + When dropping all schemas is needed, the following is the dependency order.

# Change into the parent directory to find the `dj_local_conf.json` file. 

# +
import os

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
# -

from workflow_miniscope.pipeline import lab, subject, session, miniscope

miniscope.schema.drop()
session.schema.drop()
subject.schema.drop()
lab.schema.drop()
