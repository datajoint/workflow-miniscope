import datajoint as dj
import pathlib


def get_imaging_root_data_dir():
    data_dir = dj.config.get('custom', {}).get('imaging_root_data_dir', None)
    return pathlib.Path(data_dir) if data_dir else None


def get_scan_image_files(scan_key):
    # Folder structure: root / subject / session / .tif (raw)
    data_dir = get_imaging_root_data_dir()

    from .pipeline import session
    sess_dir = data_dir / (session.SessionDirectory & scan_key).fetch1('session_dir')

    if not sess_dir.exists():
        raise FileNotFoundError(f'Session directory not found ({sess_dir})')

    tiff_filepaths = [fp.as_posix() for fp in sess_dir.glob('*.tif')]
    if tiff_filepaths:
        return tiff_filepaths
    else:
        raise FileNotFoundError(f'No .tif file found in {sess_dir}')


def get_miniscope_daq_v3_files(scan_key):
    # Folder structure: root / subject / session / .avi
    data_dir = get_imaging_root_data_dir()

    from .pipeline import session
    sess_dir = data_dir / (session.SessionDirectory & scan_key).fetch1('session_dir')

    if not sess_dir.exists():
        raise FileNotFoundError(f'Session directory not found ({sess_dir})')

    avi_filepaths = [fp.as_posix() for fp in sess_dir.glob('ms*.avi')]
    dat_filepath = sess_dir / 'timestamp.dat'
    miniscope_filepaths = avi_filepaths + [dat_filepath.as_posix()]

    if avi_filepaths and dat_filepath.exists():
        return miniscope_filepaths
    else:
        raise FileNotFoundError(f'No .avi and .dat files found in {sess_dir}')
