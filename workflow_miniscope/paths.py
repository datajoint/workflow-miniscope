import datajoint as dj


def get_miniscope_root_data_dir():
    root_data_dirs = dj.config.get('custom', {}).get('miniscope_root_data_dir', None)

    return root_data_dirs

