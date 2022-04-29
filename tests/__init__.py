# run tests: pytest -sv --cov-report term-missing --cov=workflow-miniscope -p no:warnings

import os
import pytest
import pandas as pd
import pathlib
import datajoint as dj
import importlib
import numpy as np
import sys

from workflow_miniscope.paths import get_miniscope_root_data_dir

# ------------------- SOME CONSTANTS -------------------

_tear_down = True
verbose = False

test_user_data_dir = pathlib.Path('./tests/user_data')
test_user_data_dir.mkdir(exist_ok=True)

# ------------------ GENERAL FUNCTIONS ------------------


class QuietStdOut:
    """If verbose set to false, used to quiet tear_down table.delete prints"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# ------------------- FIXTURES -------------------
@pytest.fixture(autouse=True)
def dj_config():
    if pathlib.Path('./dj_local_conf.json').exists():
        dj.config.load('./dj_local_conf.json')
    dj.config['safemode'] = False
    dj.config['custom'] = {
        'database.prefix': (os.environ.get('DATABASE_PREFIX') 
                             or dj.config['custom']['database.prefix']),
        'miniscope_root_data_dir': (os.environ.get('MINISCOPE_ROOT_DATA_DIR')
                                    or dj.config['custom']['miniscope_root_data_dir'])
    }
    return


@pytest.fixture
def pipeline():
    """ Loads workflow_miniscope.pipeline lab, session, subject, miniscope"""
    from workflow_miniscope import pipeline
    
    yield {'lab': pipeline.lab,
           'subject': pipeline.subject,
           'session': pipeline.session,
           'miniscope': pipeline.miniscope,
           'Equipment': pipeline.Equipment,
           'get_miniscope_root_data_dir': pipeline.get_miniscope_root_data_dir}

    if _tear_down:
        if verbose:
            pipeline.miniscope.Recording.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.Lab.delete()
        else:
            with QuietStdOut():
                pipeline.miniscope.Recording.delete()
                pipeline.subject.Subject.delete()
                pipeline.session.Session.delete()
                pipeline.lab.Lab.delete()
