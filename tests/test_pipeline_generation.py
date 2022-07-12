from . import dj_config, pipeline

__all__ = ["dj_config", "pipeline"]


def test_generate_pipeline(pipeline):
    subject = pipeline["subject"]
    session = pipeline["session"]
    miniscope = pipeline["miniscope"]
    Equipment = pipeline["Equipment"]

    # Test Element connection from lab, subject to Session
    assert subject.Subject.full_table_name in session.Session.parents()

    # Test Element connection from Session to miniscope
    assert session.Session.full_table_name in miniscope.Recording.parents()
    assert Equipment.full_table_name in miniscope.Recording.parents()
    assert "mask_npix" in miniscope.Segmentation.Mask.heading.secondary_attributes
    assert "activity_trace" in miniscope.Activity.Trace.heading.secondary_attributes
