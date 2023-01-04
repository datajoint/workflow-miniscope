"""Tests table population
"""


def test_recording_info(pipeline, recording_info):
    miniscope = pipeline["miniscope"]
    rel_path = recording_info["caiman_2d"]

    recording_key = (
        miniscope.RecordingInfo
        & (miniscope.RecordingInfo.File & f'file_path LIKE "%{rel_path}%"')
    ).fetch1("KEY")
    nchannels, nframes = (miniscope.RecordingInfo & recording_key).fetch1(
        "nchannels", "nframes"
    )

    assert nchannels == 1
    assert nframes == 111770


def test_processing_populate(processing, pipeline):
    miniscope = pipeline["miniscope"]
    assert len(miniscope.Processing()) == 1
