import logging
import os
from collections import abc
from contextlib import nullcontext
from pathlib import Path

import datajoint as dj
import pytest
from element_interface.utils import QuietStdOut, find_full_path, value_to_bool

# ------------------- SOME CONSTANTS -------------------

logger = logging.getLogger("datajoint")
session_dirs = ["subject1/session1"]


def pytest_addoption(parser):
    """
    Permit constants when calling pytest at command line e.g., pytest --dj-verbose False

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
        default="True",
        help="Verbose for dj items: True or False",
        choices=("True", "False"),
    )
    parser.addoption(
        "--dj-datadir",
        action="store",
        default="./tests/user_data",
        help="Relative path for saving tests data",
    )


@pytest.fixture(autouse=True, scope="session")
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
def dj_config(setup):
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

    return


@pytest.fixture(scope="function")
def element_helper_functions():
    from element_miniscope.miniscope import (
        get_loader_result,
        get_miniscope_root_data_dir,
        get_session_directory,
    )

    yield {
        "get_miniscope_root_data_dir": get_miniscope_root_data_dir,
        "get_session_directory": get_session_directory,
        "get_loader_result": get_loader_result,
    }


@pytest.fixture(autouse=True, scope="session")
def pipeline():
    """Loads workflow_miniscope.pipeline lab, session, subject, miniscope"""
    with verbose_context:
        from workflow_miniscope import pipeline

    yield {
        "lab": pipeline.lab,
        "subject": pipeline.subject,
        "session": pipeline.session,
        "miniscope": pipeline.miniscope,
        "miniscope_report": pipeline.miniscope_report,
        "Device": pipeline.Device,
        "get_miniscope_root_data_dir": pipeline.get_miniscope_root_data_dir,
        "get_session_directory": pipeline.get_session_directory,
    }

    if _tear_down:
        with verbose_context:
            pipeline.miniscope.Recording.delete()
            pipeline.miniscope_report.QualityMetrics.delete()
            pipeline.Device.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.Lab.delete()


@pytest.fixture(scope="session")
def plots(setup, pipeline):
    from element_miniscope.plotting.qc import QualityMetricFigs

    miniscope = pipeline["miniscope"]
    key = miniscope.Curation.fetch("KEY", limit=1)[0]

    yield {"qc": QualityMetricFigs(miniscope, key)}


@pytest.fixture(scope="session")
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


def populate_tables(tables):
    populate_settings = {
        "display_progress": verbose,
        "reserve_jobs": False,
        "suppress_errors": True,
    }

    with verbose_context:
        for table in tables:
            errors = table.populate(**populate_settings)

            if errors:
                logger.warning(
                    f"Populate ERROR: {len(errors)} errors in "
                    + f'"{table}.populate()" - {errors[0][-1]}'
                )


def populate_clear(tables):
    if _tear_down:
        with verbose_context:
            for table in tables:
                table.delete()


@pytest.fixture(scope="session")
def recording_info(pipeline, ingest_data):
    tables = [pipeline["miniscope"].RecordingInfo()]
    populate_tables(tables)
    yield {"caiman_2d": f"{session_dirs[0]}/0.avi"}
    populate_clear(tables)


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def processing(processing_tasks, pipeline):
    tables = [pipeline["miniscope"].Processing()]
    populate_tables(tables)
    yield
    populate_clear(tables)


@pytest.fixture(scope="session")
def curations(processing, pipeline):
    miniscope = pipeline["miniscope"]
    for key in (miniscope.Processing - miniscope.Curation).fetch("KEY"):
        miniscope.Curation().create1_from_processing_task(key)
    yield
    populate_clear([miniscope.Curation()])


@pytest.fixture(scope="session")
def post_curation(pipeline, curations):
    miniscope = pipeline["miniscope"]
    miniscope_report = pipeline["miniscope_report"]
    tables = [
        miniscope.MotionCorrection(),
        miniscope.Segmentation(),
        miniscope.Fluorescence(),
        miniscope.Activity(),
        miniscope_report.QualityMetrics(),
    ]
    populate_tables(tables)
    yield
    populate_clear(tables)
