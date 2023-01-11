from collections import abc
from typing import Union

import datajoint as dj


def get_miniscope_root_data_dir() -> Union[list, None]:
    """Return root directory for miniscope from 'miniscope_root_data_dir' config as list

    Returns:
        path (any): List of path(s) if available or None
    """
    mini_root_dirs = dj.config.get("custom", {}).get("miniscope_root_data_dir")

    if not mini_root_dirs:
        return None
    elif not isinstance(mini_root_dirs, abc.Sequence):
        return list(mini_root_dirs)
    else:
        return mini_root_dirs


def get_session_directory(session_key: dict) -> str:
    """Return relative path from SessionDirectory table given key

    Args:
        session_key (dict): Key uniquely identifying a session

    Returns:
        path (str): Relative path of session directory
    """
    from .pipeline import session

    session_dir = (session.SessionDirectory & session_key).fetch1("session_dir")
    return session_dir
