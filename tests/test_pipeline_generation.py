from . import dj_config, pipeline

__all__ = ['dj_config', 'pipeline']


def test_generate_pipeline(pipeline):
    subject = pipeline['subject']
    session = pipeline['session']
    miniscope = pipeline['miniscope']
    Equipment = pipeline['Equipment']

    subject_tbl, *_ = session.Session.parents(as_objects=True)

    # Test Element connection from lab, subject to Session
    assert subject_tbl.full_table_name == subject.Subject.full_table_name

    # Test Element connection from Session to miniscope
    session_tbl, equipment_tbl, _ = miniscope.Recording.parents(as_objects=True)
    assert session_tbl.full_table_name == session.Session.full_table_name
    assert equipment_tbl.full_table_name == Equipment.full_table_name
    assert 'mask_npix' in miniscope.Segmentation.Mask.heading.secondary_attributes
    assert 'activity_trace' in miniscope.Activity.Trace.heading.secondary_attributes
