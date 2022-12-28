from . import (
    caiman_paramset,
    curations,
    dj_config,
    ingest_sessions,
    ingest_subjects,
    pipeline,
    processing,
    processing_tasks,
    recording_info,
    sessions_csv,
    subjects_csv,
    testdata_paths,
)

__all__ = [
    "dj_config",
    "pipeline",
    "subjects_csv",
    "ingest_subjects",
    "sessions_csv",
    "ingest_sessions",
    "testdata_paths",
    "caiman_paramset",
    "recording_info",
    "processing_tasks",
    "processing",
    "curations",
]


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline["subject"]
    assert len(subject.Subject()) == 1


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    session = pipeline["session"]
    miniscope = pipeline["miniscope"]
    # get_miniscope_root_data_dir = pipeline["get_miniscope_root_data_dir"]

    assert len(session.Session()) == 1
    assert len(miniscope.Recording()) == 1

    sessions, _ = sessions_csv
    sess = sessions[1].split(",")[1]
    assert (session.SessionDirectory & {"subject": sessions[1].split(",")[0]}).fetch1(
        "session_dir"
    ) == sess


def test_paramset_insert(caiman_paramset, pipeline):
    miniscope = pipeline["miniscope"]
    from element_interface.utils import dict_to_uuid

    method, desc, paramset_hash = (
        miniscope.ProcessingParamSet & {"paramset_idx": 0}
    ).fetch1("processing_method", "paramset_desc", "param_set_hash")
    assert method == "caiman"
    assert desc == "Calcium imaging analysis with CaImAn using default parameters"
    assert dict_to_uuid(caiman_paramset) == paramset_hash
