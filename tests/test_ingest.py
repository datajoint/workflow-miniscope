"""Tests ingestion into schema tables: Lab, Subject, Session
    1. Assert length of populating data conftest
    2. Assert exact matches of inserted data fore key tables
"""
from element_interface.utils import dict_to_uuid


def test_ingest_subjects(pipeline, ingest_data):
    session = pipeline["session"]
    miniscope = pipeline["miniscope"]
    # get_miniscope_root_data_dir = pipeline["get_miniscope_root_data_dir"]

    assert len(session.Session()) == 1
    assert len(miniscope.Recording()) == 1

    sess_data = ingest_data["sessions.csv"]["content"][1].split(",")

    assert (session.SessionDirectory & {"subject": sess_data[0]}).fetch1(
        "session_dir"
    ) == sess_data[1]


def test_paramset_insert(pipeline, caiman_paramset):
    miniscope = pipeline["miniscope"]
    params_dict, params_caiman = caiman_paramset

    processing_method, paramset_desc, paramset_hash = (
        miniscope.ProcessingParamSet & {"paramset_idx": 0}
    ).fetch1("processing_method", "paramset_desc", "param_set_hash")

    assert processing_method == params_dict["processing_method"]
    assert paramset_desc == params_dict["paramset_desc"]
    assert dict_to_uuid(params_caiman) == paramset_hash
