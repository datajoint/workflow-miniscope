"""Tests Element support functions
"""
import pytest
from datajoint.errors import DataJointError


def test_root_dir(element_helper_functions):
    root_dir = element_helper_functions["get_miniscope_root_data_dir"]
    assert isinstance(root_dir(), list), "Check typing enforcement on root dir func"


def test_session_dir(pipeline, element_helper_functions):
    session = pipeline["session"]
    get_session_directory = element_helper_functions["get_session_directory"]

    key = session.SessionDirectory.fetch(limit=1, as_dict=True)[0]
    dir = key.pop("session_dir")

    assert dir == get_session_directory(key), "Check Element get_session_directory"


def test_loader(pipeline, element_helper_functions):
    from element_interface.caiman_loader import CaImAn

    get_loader_result = element_helper_functions["get_loader_result"]
    table = pipeline["miniscope"].ProcessingTask
    method, loaded_output = get_loader_result(table.fetch("KEY")[0], table)

    assert (method == "caiman") & isinstance(
        loaded_output, CaImAn
    ), "Check get_loader_result"


def test_params_insert(setup, pipeline, caiman_paramset):
    p_table = pipeline["miniscope"].ProcessingParamSet
    params_dict, params_caiman = caiman_paramset

    p_table.insert_new_params(**params_dict)  # Test re-insert of same

    params_dict.update({"paramset_id": 1})
    with pytest.raises(DataJointError) as error:
        p_table.insert_new_params(**params_dict)
    assert "name: 0" in error.value.args[0], "insert_new_params not returning orig ID"

    params_caiman.update({"decay_time": 0.3})
    params_dict.update({"paramset_id": 1, "params": params_caiman})
    p_table.insert_new_params(**params_dict)
    assert 1 in p_table.fetch("paramset_id"), "insert_new_params didn't accept new set"
