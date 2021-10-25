import pathlib

from . import (dj_config, pipeline, subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, caiman2D_paramset, caiman3D_paramset,
               scan_info, processing_tasks, processing, curations)


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline['subject']
    assert len(subject.Subject()) == 1


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    miniscope = pipeline['miniscope']
    session = pipeline['session']
    get_miniscope_root_data_dir = pipeline['get_miniscope_root_data_dir']

    assert len(session.Session()) == 1
    # assert len(scan.Scan()) == 1

    sessions, _ = sessions_csv
    sess = sessions.iloc[0]
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_miniscope_root_data_dir())
    assert (session.SessionDirectory
            & {'subject': sess.name}).fetch1('session_dir') == sess_dir.as_posix()


# def test_paramset_insert(caiman2D_paramset, caiman3D_paramset, pipeline):
#     miniscope = pipeline['miniscope']
#     from element_miniscope.imaging import dict_to_uuid

#     method, desc, paramset_hash = (imaging.ProcessingParamSet & {'paramset_idx': 1}).fetch1(
#         'processing_method', 'paramset_desc', 'param_set_hash')
#     assert method == 'caiman'
#     assert desc == 'Calcium imaging analysis' \
#                    ' with CaImAn using default CaImAn parameters for 2d planar images'
#     assert dict_to_uuid(caiman2D_paramset) == paramset_hash

#     method, desc, paramset_hash = (imaging.ProcessingParamSet & {'paramset_idx': 2}).fetch1(
#         'processing_method', 'paramset_desc', 'param_set_hash')
#     assert method == 'caiman'
#     assert desc == 'Calcium imaging analysis' \
#                    ' with CaImAn using default CaImAn parameters for 3d volumetric images'
#     assert dict_to_uuid(caiman3D_paramset) == paramset_hash
