"""Tests table population
"""
import pytest


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


def test_processing_populate(pipeline, processing):
    miniscope = pipeline["miniscope"]
    assert len(miniscope.Processing()) == 1


def test_curation_populate(pipeline, curations):
    miniscope = pipeline["miniscope"]
    assert len(miniscope.Curation()) == 1


def test_results(pipeline, post_curation):
    mini = pipeline["miniscope"]
    report = pipeline["miniscope_report"]

    names = ["MotionCorrection average image", "Fluorescence Trace", "Activity Trace"]
    means = [
        mini.MotionCorrection.Summary.fetch("average_image", limit=1)[0][0][0].mean(),
        mini.Fluorescence.Trace.fetch("fluorescence", limit=1)[0].mean(),
        mini.Activity.Trace.fetch("activity_trace", limit=1)[0].mean(),
        report.QualityMetrics.fetch("r_values", limit=1)[0].mean(),
    ]
    expected = [27.94, 335, 335, 0.448]
    permitted_delta = [0.1, 1, 1, 0.01]

    for n, m, e, d in zip(names, means, expected, permitted_delta):
        assert m == pytest.approx(  # assert mean is within delta of expected value
            e, d
        ), f"Issues with data for {n}. Expected {e} ±{d}, Found {m}"


def test_plots(pipeline, plots, post_curation):
    metrics = pipeline["miniscope_report"].QualityMetrics
    qc = plots["qc"]

    assert all(
        metrics.fetch("cnn_preds")[0] == qc.components.cnn_preds
    ), "Report schema and QC fig didn't load the same estimates"
