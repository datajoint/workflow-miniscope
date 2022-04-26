import datajoint as dj

from element_lab import lab
from element_animal import subject
from element_session import session_with_datetime as session
from element_miniscope import miniscope

from element_lab.lab import Source, Lab, Protocol, User, Location, Project
from element_animal.subject import Subject
from element_session.session_with_datetime import Session

from .paths import get_miniscope_root_data_dir, get_session_directory

if 'custom' not in dj.config:
    dj.config['custom'] = {}

db_prefix = dj.config['custom'].get('database.prefix', '')


# Activate `lab`, `subject`, `session` schema ------------------------------------------

lab.activate(db_prefix + 'lab')

subject.activate(db_prefix + 'subject', linking_module=__name__)

Experimenter = lab.User
session.activate(db_prefix + 'session', linking_module=__name__)


# Declare table `Equipment` and `AnatomicalLocation` for use in element_miniscope ------

@lab.schema
class Equipment(dj.Manual):
    definition = """
    acquisition_hardware: varchar(32) 
    """

@lab.schema
class AnatomicalLocation(dj.Manual):
    definition = """
    recording_location_id : varchar(16)
    ----
    anatomical_description: varchar(256)
    """

# Activate `miniscope` schema ----------------------------------------------------------

miniscope.activate(db_prefix + 'miniscope',  linking_module=__name__)
