import logging
import os
from collections import abc
from contextlib import nullcontext
from pathlib import Path

import datajoint as dj
import djarchive_client
import pytest
from element_interface.utils import (
    QuietStdOut,
    find_full_path,
    value_to_bool,
    write_csv,
)

from workflow_miniscope.ingest import ingest_sessions, ingest_subjects

# ------------------- SOME CONSTANTS -------------------

logger = logging.getLogger("datajoint")
session_dirs = ["subject1/session1"]
# pytest_plugins = "cov"


def pytest_addoption(parser):
    """
    Permit constants when calling pytest at commandline e.g., pytest --dj-verbose False

    Arguments:
        --dj-verbose (bool):  Default True. Pass print statements from Elements.
        --dj-teardown (bool): Default True. Delete pipeline on close.
        --dj-datadir (str):  Default ./tests/user_data. Relative path of test CSV data.
    """
    parser.addoption(
        "--dj-verbose",
        action="store",
        default="True",
        help="Verbose for dj items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--dj-teardown",
        action="store",
        default="False",  # "True", # TODO: default true
        help="Verbose for dj items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--dj-datadir",
        action="store",
        default="./tests/user_data",
        help="Relative path for saving tests data",
    )


@pytest.fixture(scope="session")
def setup(request):
    """Take passed commandline variables, set as global"""
    global verbose, _tear_down, test_user_data_dir, verbose_context

    verbose = value_to_bool(request.config.getoption("--dj-verbose"))
    _tear_down = value_to_bool(request.config.getoption("--dj-teardown"))
    test_user_data_dir = Path(request.config.getoption("--dj-datadir"))
    test_user_data_dir.mkdir(exist_ok=True)

    if not verbose:
        logging.getLogger("datajoint").setLevel(logging.CRITICAL)

    verbose_context = nullcontext() if verbose else QuietStdOut()

    yield verbose_context, verbose


# ------------------- FIXTURES -------------------


@pytest.fixture(autouse=True, scope="session")
def dj_config():
    """If dj_local_config exists, load"""
    if Path("./dj_local_conf.json").exists():
        dj.config.load("./dj_local_conf.json")

    dj.config.update(
        {
            "safemode": False,
            "database.host": os.environ.get("DJ_HOST") or dj.config["database.host"],
            "database.password": os.environ.get("DJ_PASS")
            or dj.config["database.password"],
            "database.user": os.environ.get("DJ_USER") or dj.config["database.user"],
            "custom": {
                "database.prefix": os.environ.get("DATABASE_PREFIX")
                or dj.config["custom"]["database.prefix"],
                "miniscope_root_data_dir": (
                    os.environ.get("MINISCOPE_ROOT_DATA_DIR")
                    or dj.config["custom"]["miniscope_root_data_dir"]
                ),
            },
        }
    )

    return


@pytest.fixture(scope="session")
def test_data(setup, dj_config):
    mini_root_dirs = dj.config["custom"]["miniscope_root_data_dir"]

    test_data_exists = all(
        find_full_path(mini_root_dirs, p).exists() for p in session_dirs
    )

    if not test_data_exists:

        if not isinstance(mini_root_dirs, abc.Sequence):
            mini_root_dirs = list(mini_root_dirs)

        djarchive_client.client().download(
            "workflow-miniscope-test-set",
            "v1",
            str(mini_root_dirs[0]),
            create_target=False,
        )
    return


@pytest.fixture(autouse=True, scope="session")
def pipeline(setup):
    """Loads workflow_miniscope.pipeline lab, session, subject, miniscope"""
    with verbose_context:
        from workflow_miniscope import pipeline

    yield {
        "lab": pipeline.lab,
        "subject": pipeline.subject,
        "session": pipeline.session,
        "miniscope": pipeline.miniscope,
        "Device": pipeline.Device,
        "get_miniscope_root_data_dir": pipeline.get_miniscope_root_data_dir,
    }

    if _tear_down:
        with verbose_context:
            pipeline.miniscope.Recording.delete()
            pipeline.Device.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.Lab.delete()


@pytest.fixture(scope="session")
def ingest_data(setup, pipeline, test_data):
    """For each input, generates csv in test_user_data_dir and ingests in schema"""
    # CSV as list of 3: filename, relevant tables, content
    all_csvs = {
        "subjects.csv": {
            "func": ingest_subjects,
            "content": [
                "subject,sex,subject_birth_date,subject_description",
                "subject1,M,2021-01-01 00:00:01,Theo",
            ],
        },
        "sessions.csv": {
            "func": ingest_sessions,
            "content": [
                "subject,session_dir,acq_software",
                f"subject1,{session_dirs[0]},Miniscope-DAQ-V4",
            ],
        },
    }
    # If data in last table, presume didn't tear down last time, skip insert
    if len(pipeline["miniscope"].Recording()) == 0:
        for csv_filename, csv_dict in all_csvs.items():
            csv_path = test_user_data_dir / csv_filename  # add prefix for rel path
            write_csv(csv_path, csv_dict["content"])  # write content at rel path
            csv_dict["funct"](csv_path, verbose=verbose, skip_duplicates=True)

    yield all_csvs

    if _tear_down:
        with verbose_context:
            for csv_info in all_csvs:
                csv_path = test_user_data_dir / csv_info[1]
                csv_path.unlink()


@pytest.fixture
def caiman_paramset(pipeline):
    miniscope = pipeline["miniscope"]

    params_caiman = dict(
        decay_time=0.4,
        pw_rigid=False,
        max_shifts=(5, 5),
        gSig_filt=(3, 3),
        strides=(48, 48),
        overlaps=(24, 24),
        max_deviation_rigid=3,
        border_nan="copy",
        method_init="corr_pnr",
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
        method_deconvolution="oasis",
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

    params_dict = dict(
        processing_method="caiman",
        paramset_id=0,
        paramset_desc="Calcium imaging analysis with CaImAn using default parameters",
        params=params_caiman,
    )

    miniscope.ProcessingParamSet.insert_new_params(**params_dict)

    yield params_dict, params_caiman

    if _tear_down:
        with verbose_context:
            (miniscope.ProcessingParamSet & "paramset_id = 0").delete()


@pytest.fixture
def recording_info(pipeline, ingest_data):
    miniscope = pipeline["miniscope"]

    miniscope.RecordingInfo.populate()

    yield {"caiman_2d": f"{session_dirs[0]}/0.avi"}

    if _tear_down:
        with verbose_context:
            miniscope.RecordingInfo.delete()


@pytest.fixture
def processing_tasks(pipeline, caiman_paramset, recording_info):
    miniscope = pipeline["miniscope"]
    session = pipeline["session"]
    get_miniscope_root_data_dir = pipeline["get_miniscope_root_data_dir"]

    for scan_key in (
        session.Session * miniscope.Recording - miniscope.ProcessingTask
    ).fetch("KEY"):
        scan_file = find_full_path(
            get_miniscope_root_data_dir(),
            (miniscope.RecordingInfo.File & scan_key).fetch("file_path")[0],
        )

        recording_dir = scan_file.parent
        caiman_dir = Path(recording_dir / "caiman")
        if caiman_dir.exists():
            miniscope.ProcessingTask.insert1(
                {**scan_key, "paramset_id": 0, "processing_output_dir": caiman_dir}
            )

    yield

    if _tear_down:
        with verbose_context:
            miniscope.ProcessingTask.delete()


@pytest.fixture
def processing(processing_tasks, pipeline):
    miniscope = pipeline["miniscope"]

    errors = miniscope.Processing.populate(suppress_errors=True)

    if errors:
        logger.warning(
            f"Populate ERROR: {len(errors)} errors in "
            + f'"miniscope.Processing.populate()" - {errors[0][-1]}'
        )

    yield

    if _tear_down:
        with verbose_context:
            miniscope.Processing.delete()


@pytest.fixture
def curations(processing, pipeline):
    miniscope = pipeline["miniscope"]

    for key in (miniscope.Processing - miniscope.Curation).fetch("KEY"):
        miniscope.Curation().create1_from_processing_task(key)

    yield

    if _tear_down:
        with verbose_context:
            miniscope.Curation.delete()
