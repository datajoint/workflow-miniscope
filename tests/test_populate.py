from . import (dj_config, pipeline, subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions, testdata_paths, caiman_paramset,
               recording_info, processing_tasks, processing, curations)

__all__ = ['dj_config', 'pipeline', 'subjects_csv', 'ingest_subjects', 'sessions_csv',
           'ingest_sessions', 'testdata_paths', 'caiman_paramset', 'recording_info',
           'processing_tasks', 'processing', 'curations']


def test_recording_info_populate(testdata_paths, pipeline, recording_info):
    miniscope = pipeline['miniscope']
    rel_path = testdata_paths['caiman_2d']
    scan_key = (miniscope.RecordingInfo & (miniscope.RecordingInfo.File
                                           & f'file_path LIKE "%{rel_path}%"')
                ).fetch1('KEY')
    nchannels, nframes = (miniscope.RecordingInfo & scan_key
                          ).fetch1('nchannels', 'nframes')

    assert nchannels == 1
    assert nframes == 111770


def test_processing_populate(processing, pipeline):
    miniscope = pipeline['miniscope']
    assert len(miniscope.Processing()) == 1
