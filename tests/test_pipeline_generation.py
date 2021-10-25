from . import (dj_config, pipeline, subjects_csv, ingest_subjects, sessions_csv, ingest_sessions,
               testdata_paths, caiman2D_paramset, processing_tasks, processing, curations)


def test_generate_pipeline(pipeline):
    miniscope = pipeline['miniscope']
    session = pipeline['session']
    Equipment = pipeline['Equipment']
    subject = pipeline['subject']

    subject_tbl, *_ = session.Session.parents(as_objects=True)

    # test elements connection from lab, subject to Session
    assert subject_tbl.full_table_name == subject.Subject.full_table_name

    # # test elements connection from Session to miniscope
    session_tbl, equipment_tbl, acquisitionsoftware_tbl = miniscope.Recording.parents(as_objects=True)
    assert session_tbl.full_table_name == session.Session.full_table_name
    assert equipment_tbl.full_table_name == Equipment.full_table_name
    assert acquisitionsoftware_tbl.full_table_name == miniscope.AcquisitionSoftware.full_table_name
