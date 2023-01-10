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

# + [markdown] tags=[]
# # DataJoint U24 - Workflow Miniscope
#

# + [markdown] tags=[]
# ## Setup
#
# -

# First, let's change directories to find the `dj_local_conf` file.
#

# +
import os
import numpy as np
import datajoint as dj

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
dj.config["custom"]["database.prefix"] = "u24_mini_"
# -

# Next, we populate the python namespace with the required schemas
#

from workflow_miniscope.pipeline import miniscope, QualityMetricFigs

# + [markdown] jp-MarkdownHeadingCollapsed=true jp-MarkdownHeadingCollapsed=true tags=[]
# ## Visualizations
#
# CaImAn produces a few metrics for estimates. These can be visualized as follows.
#
# -

key = miniscope.Curation.fetch("KEY", limit=1)[0]
qm = QualityMetricFigs(miniscope, key, dark_mode=True)
print("Available plots:", qm.plot_list)
fig = qm.get_single_fig("r_values")
fig.show(
    "png"
)  # .show('png') is optional. Here, it is used to render the image within a notebook that is embedded in a browser.qm.get_grid()

# A number of metrics are available from CaImAn estimates.

# +
import inspect

[
    i[0]
    for i in inspect.getmembers(qm.estimates)  # see all available class attributes
    if not i[0].startswith("_") and not inspect.ismethod(i[1])  # filter out functions
]
# -

#  We can adjust which we visualize using the following syntax.

qm.component_list = ["r_values", "SNR_comp", "cnn_preds", "neurons_sn"]
noise = qm.components.neurons_sn
qm.plots = {
    "neurons_sn": {
        "xaxis": "Noise Std",
        "data": qm.components.neurons_sn,
        "bins": np.linspace(min(noise), max(noise), 10),
        "vline": noise.mean(),
    }
}
fig = qm.get_grid(n_columns=4)
fig.show("png")

qm.components


