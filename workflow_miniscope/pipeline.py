import datajoint as dj
from element_lab import lab
from element_animal import subject
from element_session import session_with_datetime as session
from element_miniscope import miniscope

from element_lab.lab import Source, Lab, Protocol, User, Location, Project
from element_animal.subject import Subject
from element_session.session_with_datetime import Session

from .paths import get_miniscope_root_data_dir


if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')


# Activate `lab`, `subject`, `session` schema ------------------------------------------

lab.activate(db_prefix + 'lab')

subject.activate(db_prefix + 'subject', linking_module=__name__)

Experimenter = lab.User
session.activate(db_prefix + 'session', linking_module=__name__)


# Declare table `Equipment` for use in element_miniscope -------------------------------

@lab.schema
class Equipment(dj.Manual):
    definition = """
    scanner: varchar(32) 
    """


# Activate `miniscope` schema ----------------------------------------------------------

miniscope.activate(db_prefix + 'miniscope',  linking_module=__name__)
