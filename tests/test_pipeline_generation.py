"""Tests table architecture and connections: Subject, Session, Miniscope
"""


def test_upstream_pipeline(pipeline):
    session = pipeline["session"]
    subject = pipeline["subject"]

    # test connection Subject->Session
    assert subject.Subject.full_table_name == session.Session.parents()[0]

    # test required attribute
    assert "session_dir" in session.SessionDirectory.heading.secondary_attributes


def test_miniscope_pipeline(pipeline):
    session = pipeline["session"]
    miniscope = pipeline["miniscope"]
    Device = pipeline["Device"]

    # test connection miniscope.Recording
    recording_parent_links = miniscope.Recording.parents()
    recording_parent_list = [session.Session, Device, miniscope.AcquisitionSoftware]
    for parent in recording_parent_list:
        assert (
            parent.full_table_name in recording_parent_links
        ), f"miniscope.Recording.parents() did not include {parent.full_table_name}"

    # test attributes
    assert "mask_npix" in miniscope.Segmentation.Mask.heading.secondary_attributes
    assert "activity_trace" in miniscope.Activity.Trace.heading.secondary_attributes
