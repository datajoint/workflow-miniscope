# DataJoint Workflow - Miniscope

Workflow for miniscope calcium imaging data acquired with miniature microscopes (e.g. 
[UCLA Miniscope](https://github.com/Aharoni-Lab/Miniscope-v4)) using the 
[Miniscope-DAQ](https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software) acquisition 
software and processed with [CaImAn](https://github.com/flatironinstitute/CaImAn).

A complete miniscope workflow can be built using the DataJoint Elements:
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-miniscope](https://github.com/datajoint/element-miniscope)

This repository provides demonstrations for:
1. Set up a workflow using DataJoint Elements (see 
[workflow_miniscope/pipeline.py](workflow_miniscope/pipeline.py))
2. Ingestion of data/metadata based on a predefined file structure, file naming 
convention, and directory lookup methods (see 
[workflow_miniscope/ingest.py](workflow_miniscope/ingest.py))
3. Processing results.

See the [DataJoint Elements](https://github.com/datajoint/datajoint-elements) 
repository for descriptions of the other `elements` and `workflows` developed as part 
of this National Institutes of Health (NIH)-funded initiative.

## Workflow architecture

+ The miniscope calcium imaging workflow presented here uses components from four 
DataJoint Elements ([element-lab](https://github.com/datajoint/element-lab),
 [element-animal](https://github.com/datajoint/element-animal), 
 [element-session](https://github.com/datajoint/element-session) and 
 [element-miniscope](https://github.com/datajoint/element-miniscope)) assembled 
 together to form a fully functional workflow.

## Installation instructions

+ The installation instructions can be found at the 
[datajoint-elements repository](
    https://github.com/datajoint/datajoint-elements/blob/main/gh-pages/docs/usage/install.md).

## Interacting with the DataJoint workflow

+ Please refer to the following workflow-specific 
 [Jupyter notebooks](/notebooks) for an in-depth explanation of how to run the 
 workflow ([03-process.ipynb](notebooks/03-process.ipynb)) and explore the data 
 ([05-explore.ipynb](notebooks/05-explore.ipynb)).