import pathlib

from . import (dj_config, pipeline, subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, caiman2D_paramset, caiman3D_paramset,
               scan_info, processing_tasks, processing, curations)


__all__ = ['dj_config', 'pipeline', 'subjects_csv', 'ingest_subjects', 'sessions_csv',
           'ingest_sessions', 'testdata_paths', 'caiman2D_paramset',
           'caiman3D_paramset', 'scan_info', 'processing_tasks', 'processing',
           'curations']


def test_ingest_subjects(pipeline, ingest_subjects):
    subject = pipeline['subject']
    assert len(subject.Subject()) == 1


def test_ingest_sessions(pipeline, sessions_csv, ingest_sessions):
    session = pipeline['session']
    get_miniscope_root_data_dir = pipeline['get_miniscope_root_data_dir']

    assert len(session.Session()) == 1

    sessions, _ = sessions_csv
    sess = sessions.iloc[3]
    sess_dir = pathlib.Path(sess.session_dir).relative_to(get_miniscope_root_data_dir())
    assert (session.SessionDirectory
            & {'subject': sess.name}).fetch1('session_dir') == sess_dir.as_posix()


def test_paramset_insert(caiman2D_paramset, pipeline):
    miniscope = pipeline['miniscope']
    from element_interface.utils import dict_to_uuid

    method, desc, paramset_hash = (miniscope.ProcessingParamSet & {'paramset_idx': 1}
                                   ).fetch1('processing_method', 'paramset_desc',
                                            'param_set_hash')
    assert method == 'caiman'
    assert desc == 'Calcium imaging analysis with CaImAn using default parameters'
    assert dict_to_uuid(caiman2D_paramset) == paramset_hash
