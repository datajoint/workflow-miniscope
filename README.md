# DataJoint Workflow for Miniscope Calcium Imaging

The DataJoint Workflow for miniscope calcium imaging data acquired with miniature
microscopes (e.g. [UCLA Miniscope](https://github.com/Aharoni-Lab/Miniscope-v4)) using
the [Miniscope-DAQ](https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software)
acquisition software and processed with
[CaImAn](https://github.com/flatironinstitute/CaImAn). DataJoint Elements collectively
standardize and automate data collection and analysis for neuroscience experiments. Each
Element is a modular pipeline for data storage and processing with corresponding
database tables that can be combined with other Elements to assemble a fully functional
pipeline.  This repository also provides a tutorial notebook to learn the pipeline.

## Experiment Flowchart

![flowchart](https://raw.githubusercontent.com/datajoint/element-miniscope/main/images/flowchart.svg)

## Data Pipeline Diagram

![pipeline](https://raw.githubusercontent.com/datajoint/element-miniscope/main/images/pipeline_imaging.svg)

## Getting Started

+ [Interactive tutorial](#interactive-tutorial)

+ Install Element Miniscope from PyPI

     ```bash
     pip install element-miniscope
     ```

+ [Documentation](https://datajoint.com/docs/elements/element-miniscope)

## Support

+ If you need help getting started or run into any errors, please contact our team by email at support@datajoint.com.

## Interactive Tutorial

### Launch Environment

+ Local Environment
  + Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  + Install [VSCode](https://code.visualstudio.com/)
  + Install [Conda](https://docs.conda.io/en/latest/miniconda.html)
  + Install [Mamba](https://mamba.readthedocs.io/en/latest/installation.html)
  + Install [CaImAn](https://caiman.readthedocs.io/en/master/Installation.html)
  + Configure a database.  See [here](https://tutorials.datajoint.org/setting-up/local-database.html) for details.
  + `git clone` the code repository and open it in VSCode
  + Install the repository with `pip install -e .`
  + Setup a `dj_local_conf.json` with the `database.prefix` and `miniscope_root_data_dir`. See [User Guide](https://datajoint.com/docs/elements/user-guide/) for details.
  + Add your example data to the `miniscope_root_data_dir`.

### Instructions

1. We recommend you start by navigating to the `notebooks` directory. Execute the cells in the notebooks to begin your walk through of the tutorial.
