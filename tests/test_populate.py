import numpy as np

from . import (dj_config, pipeline, subjects_csv, ingest_subjects,
               sessions_csv, ingest_sessions,
               testdata_paths, caiman2D_paramset, caiman3D_paramset,
               scan_info, processing_tasks, processing, curations)


def test_scan_info_populate_scanimage_2D(testdata_paths, pipeline, scan_info):
    scan = pipeline['scan']
    rel_path = testdata_paths['scanimage_2d']
    scan_key = (scan.ScanInfo & (scan.ScanInfo.ScanFile
                                 & f'file_path LIKE "%{rel_path}%"')).fetch1('KEY')
    nfields, nchannels, ndepths, nframes = (scan.ScanInfo & scan_key).fetch1(
        'nfields', 'nchannels', 'ndepths', 'nframes')

    assert nfields == 1
    assert nchannels == 2
    assert ndepths == 1
    assert nframes == 25000


def test_scan_info_populate_scanimage_3D(testdata_paths, pipeline, scan_info):
    scan = pipeline['scan']
    rel_path = testdata_paths['scanimage_3d']
    scan_key = (scan.ScanInfo & (scan.ScanInfo.ScanFile
                                 & f'file_path LIKE "%{rel_path}%"')).fetch1('KEY')
    nfields, nchannels, ndepths, nframes = (scan.ScanInfo & scan_key).fetch1(
        'nfields', 'nchannels', 'ndepths', 'nframes')

    assert nfields == 3
    assert nchannels == 2
    assert ndepths == 3
    assert nframes == 2000


def test_processing_populate(processing, pipeline):
    imaging = pipeline['imaging']
    assert len(imaging.Processing()) == 5