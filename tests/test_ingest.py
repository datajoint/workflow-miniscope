from element_interface.utils import find_full_path, find_root_directory

from . import (dj_config, pipeline, subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, caiman2D_paramset, recording_info, processing_tasks,
               processing, curations)


__all__ = ['dj_config', 'pipeline', 'subjects_csv', 'ingest_subjects', 'sessions_csv',
           'ingest_sessions', 'testdata_paths', 'caiman2D_paramset',
           'recording_info', 'processing_tasks', 'processing', 'curations']


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline['subject']
    assert len(subject.Subject()) == 1


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    session = pipeline['session']
    get_miniscope_root_data_dir = pipeline['get_miniscope_root_data_dir']

    assert len(session.Session()) == 1

    sessions, _ = sessions_csv
    sess = sessions[1].split(",")[1]
    sess_dir_full = find_full_path(get_miniscope_root_data_dir(), sess)
    root_dir = find_root_directory(get_miniscope_root_data_dir(), sess_dir_full)
    sess_dir = sess_dir_full.relative_to(root_dir)
    assert (session.SessionDirectory
            & {'subject': sessions[1].split(",")[0]}
            ).fetch1('session_dir') == str(sess_dir)


def test_paramset_insert(caiman2D_paramset, pipeline):
    miniscope = pipeline['miniscope']
    from element_interface.utils import dict_to_uuid

    method, desc, paramset_hash = (miniscope.ProcessingParamSet & {'paramset_idx': 1}
                                   ).fetch1('processing_method', 'paramset_desc',
                                            'param_set_hash')
    assert method == 'caiman'
    assert desc == 'Calcium imaging analysis with CaImAn using default parameters'
    assert dict_to_uuid(caiman2D_paramset) == paramset_hash
