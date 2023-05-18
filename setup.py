#!/usr/bin/env python
from os import path

from setuptools import find_packages, setup

pkg_name = "workflow_miniscope"
here = path.abspath(path.dirname(__file__))

long_description = """"
# Workflow for miniscope calcium imaging data acquired with Miniscope-DAQ-V3/V4 software and analyzed with CaImAn.

Build a complete imaging workflow using the DataJoint Elements
+ [element-lab](https://github.com/datajoint/element-lab)
+ [element-animal](https://github.com/datajoint/element-animal)
+ [element-session](https://github.com/datajoint/element-session)
+ [element-miniscope](https://github.com/datajoint/element-miniscope)
"""

with open(path.join(here, "requirements.txt")) as f:
    requirements = f.read().splitlines()

with open(path.join(here, pkg_name, "version.py")) as f:
    exec(f.read())

setup(
    name="workflow-miniscope",
    version=__version__,  # noqa: F821
    description="Miniscope calcium imaging workflow using the DataJoint Elements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DataJoint",
    author_email="info@datajoint.com",
    license="MIT",
    url="https://github.com/datajoint/workflow-miniscope",
    keywords="neuroscience datajoint calcium-imaging miniscope",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=requirements,
)
