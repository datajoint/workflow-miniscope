import datajoint as dj

from . import db_prefix

schema = dj.Schema(db_prefix + "reference")


@schema
class Device(dj.Lookup):
    """Table for managing lab Devices.

    Attributes:
        device ( varchar(32) ): Device short name.
        modality ( varchar(64) ): Modality for which this device is used.
        description ( varchar(256) ): Optional. Description of device.
    """

    definition = """
    device             : varchar(32)
    ---
    modality           : varchar(64)
    description=''     : varchar(256)
    """
    contents = [
        ["Miniscope_V4_BNO", "Miniscope", "V4 Miniscope with head orientation sensor."],
    ]


@schema
class AnatomicalLocation(dj.Manual):
    """Lookup table for anatomical location

    Attributes:
        recording_location_id  ( varchar(16) ): Lookup id for location
        anatomical_description ( varchar(256) ): Location full description
    """

    definition = """
    recording_location_id : varchar(16) # Lookup id for location
    ---
    anatomical_description: varchar(256) # Location full description
    """
