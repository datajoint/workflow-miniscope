import datajoint as dj
from collections import abc


def get_miniscope_root_data_dir():
    mini_root_dirs = dj.config.get("custom", {}).get("miniscope_root_data_dir")
    if not mini_root_dirs:
        return None
    elif not isinstance(mini_root_dirs, abc.Sequence):
        return list(mini_root_dirs)
    else:
        return mini_root_dirs


def get_session_directory(session_key: dict) -> str:
    from .pipeline import session

    session_dir = (session.SessionDirectory & session_key).fetch1("session_dir")
    return session_dir
