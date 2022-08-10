"""
run all tests:
    pytest -sv --cov-report term-missing --cov=workflow_miniscope -p no:warnings tests/
run one test, debug:
    pytest [above options] --pdb tests/tests_name.py -k function_name
"""

import os
import sys
import pytest
import pathlib
import datajoint as dj
from contextlib import nullcontext
from element_interface.utils import find_full_path


# ------------------- SOME CONSTANTS -------------------

_tear_down = True
verbose = False

test_user_data_dir = pathlib.Path("./tests/user_data")
test_user_data_dir.mkdir(exist_ok=True)

sessions_dirs = ["subject1/session1"]

# ------------------ GENERAL FUNCTIONS ------------------


def write_csv(content, path):
    """
    General function for writing strings to lines in CSV
    :param path: pathlib PosixPath
    :param content: list of strings, each as row of CSV
    """
    with open(path, "w") as f:
        for line in content:
            f.write(line + "\n")


class QuietStdOut:
    """If verbose set to false, used to quiet tear_down table.delete prints"""

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


verbose_context = nullcontext() if verbose else QuietStdOut()

# ------------------- FIXTURES -------------------


@pytest.fixture(autouse=True)
def dj_config():
    if pathlib.Path("./dj_local_conf.json").exists():
        dj.config.load("./dj_local_conf.json")
    dj.config["safemode"] = False
    dj.config["database.use_tls"] = False
    dj.config["custom"] = {
        "database.prefix": (
            os.environ.get("DATABASE_PREFIX") or dj.config["custom"]["database.prefix"]
        ),
        "miniscope_root_data_dir": (
            os.environ.get("MINISCOPE_ROOT_DATA_DIR")
            or dj.config["custom"]["miniscope_root_data_dir"]
        ),
    }
    return


@pytest.fixture(autouse=True)
def test_data(dj_config):
    mini_root_dirs = dj.config["custom"]["miniscope_root_data_dir"]

    test_data_exists = all(
        find_full_path(mini_root_dirs, p).exists() for p in sessions_dirs
    )

    if not test_data_exists:
        import djarchive_client
        from collections import abc

        if not isinstance(mini_root_dirs, abc.Sequence):
            mini_root_dirs = list(mini_root_dirs)
        djarchive_client.client().download(
            "workflow-miniscope-test-set",
            "v1",
            str(mini_root_dirs[0]),
            create_target=False,
        )
    return


@pytest.fixture
def pipeline():
    """Loads workflow_miniscope.pipeline lab, session, subject, miniscope"""
    with verbose_context:
        from workflow_miniscope import pipeline

    yield {
        "lab": pipeline.lab,
        "subject": pipeline.subject,
        "session": pipeline.session,
        "miniscope": pipeline.miniscope,
        "Equipment": pipeline.Equipment,
        "get_miniscope_root_data_dir": pipeline.get_miniscope_root_data_dir,
    }

    if _tear_down:
        with verbose_context:
            pipeline.miniscope.Recording.delete()
            pipeline.subject.Subject.delete()
            pipeline.session.Session.delete()
            pipeline.lab.Lab.delete()


@pytest.fixture
def subjects_csv():
    """Create a 'subjects.csv' file"""
    subject_content = [
        "subject,sex,subject_birth_date,subject_description",
        "subject1,M,2021-01-01 00:00:01,Theo",
    ]
    subject_csv_path = pathlib.Path("./tests/user_data/subjects.csv")
    write_csv(subject_content, subject_csv_path)

    yield subject_content, subject_csv_path
    if _tear_down:
        with verbose_context:
            subject_csv_path.unlink()


@pytest.fixture
def ingest_subjects(pipeline, subjects_csv):
    from workflow_miniscope.ingest import ingest_subjects

    _, subjects_csv_path = subjects_csv
    # if not tear_down, skip duplicates
    skip_duplicates = not _tear_down
    ingest_subjects(subjects_csv_path, verbose=verbose, skip_duplicates=skip_duplicates)
    return


@pytest.fixture
def sessions_csv():
    """Create a 'sessions.csv' file"""
    session_csv_path = pathlib.Path("./tests/user_data/sessions.csv")
    session_content = [
        "subject,session_dir,acquisition_software",
        "subject1,subject1/session1,Miniscope-DAQ-V4",
    ]
    write_csv(session_content, session_csv_path)

    yield session_content, session_csv_path
    if _tear_down:
        with verbose_context:
            session_csv_path.unlink()


@pytest.fixture
def ingest_sessions(ingest_subjects, sessions_csv):
    from workflow_miniscope.ingest import ingest_sessions

    _, sessions_csv_path = sessions_csv
    ingest_sessions(sessions_csv_path, verbose=verbose)
    return


@pytest.fixture
def testdata_paths():
    return {"caiman_2d": "subject1/session1/0.avi"}


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

    miniscope.ProcessingParamSet.insert_new_params(
        processing_method="caiman",
        paramset_id=0,
        paramset_desc="Calcium imaging analysis with CaImAn using default parameters",
        params=params_caiman,
    )

    yield params_caiman

    if _tear_down:
        with verbose_context:
            (miniscope.ProcessingParamSet & "paramset_id = 0").delete()


@pytest.fixture
def recording_info(pipeline, ingest_sessions):
    miniscope = pipeline["miniscope"]

    miniscope.RecordingInfo.populate()

    yield

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
        caiman_dir = pathlib.Path(recording_dir / "caiman")
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
        print(
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
