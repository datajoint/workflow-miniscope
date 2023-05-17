import datajoint as dj
from element_animal import subject
from element_animal.subject import Subject
from element_event import event, trial
from element_lab import lab
from element_lab.lab import Lab, Project, Protocol, Source, User
from element_miniscope import miniscope, miniscope_report
from element_session import session_with_datetime as session
from element_session.session_with_datetime import Session

from .paths import get_miniscope_root_data_dir, get_session_directory
from .reference import AnatomicalLocation, Device

if "custom" not in dj.config:
    dj.config["custom"] = {}

db_prefix = dj.config["custom"].get("database.prefix", "")

__all__ = [
    "lab",
    "subject",
    "session",
    "trial",
    "event",
    "miniscope",
    "miniscope_report",
    "Source",
    "Lab",
    "Protocol",
    "User",
    "Device",
    "AnatomicalLocation",
    "Project",
    "Subject",
    "Session",
    "get_miniscope_root_data_dir",
    "get_session_directory",
]

# Activate schemas

Experimenter = lab.User
lab.activate(db_prefix + "lab")
subject.activate(db_prefix + "subject", linking_module=__name__)
session.activate(db_prefix + "session", linking_module=__name__)
trial.activate(db_prefix + "trial", db_prefix + "event", linking_module=__name__)
miniscope.activate(db_prefix + "miniscope", linking_module=__name__)
