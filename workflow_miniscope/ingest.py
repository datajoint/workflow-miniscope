import csv
import json
import logging
import pathlib
from datetime import datetime

from element_interface.utils import find_full_path, ingest_csv_to_table

from .paths import get_miniscope_root_data_dir
from .pipeline import Device, event, miniscope, session, subject, trial

logger = logging.getLogger("datajoint")


def ingest_subjects(
    subject_csv_path: str = "./user_data/subjects.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest subjects listed in the subject column of ./user_data/subjects.csv

    Args:
        subject_csv_path (str, optional): Relative path to subject csv.
            Defaults to "./user_data/subjects.csv".
        skip_duplicates (bool, optional): See DataJoint `insert` function. Default True.
        verbose (bool, optional): Print number inserted (i.e., table length change).
            Defaults to True.
    """
    csvs = [subject_csv_path]
    tables = [subject.Subject()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def ingest_sessions(
    session_csv_path: str = "./user_data/sessions.csv",
    skip_duplicates: bool = False,
    verbose: bool = True,
):
    """Ingest session list from csv

    Args:
        session_csv_path (str, optional): Relative path to CSV of sessions.
            Defaults to "./user_data/sessions.csv".
        skip_duplicates (bool, optional): See DataJoint `insert` function. Default False.
        verbose (bool, optional): Print number inserted. Defaults to True.

    Raises:
        NotImplementedError: Only software Miniscope-DAQ-V3 or V4 implemented
        FileNotFoundError: No .avi files found in session path
    """
    if not verbose:  # If non verbose, set logging to warn, reset later
        prev_loglevel = logger.level
        logger.setLevel("WARN")

    logger.info("---- Insert new `Session` and `Recording` ----")

    with open(session_csv_path, newline="") as f:
        input_sessions = list(csv.DictReader(f, delimiter=","))

    session_list, session_dir_list, recording_list, hardware_list = [], [], [], []

    for single_session in input_sessions:
        acq_software = single_session["acq_software"]
        if acq_software not in ["Miniscope-DAQ-V3", "Miniscope-DAQ-V4"]:
            raise NotImplementedError(
                f"Not implemented for acquisition software of " f"type {acq_software}."
            )

        # Folder structure: root / subject / session / .avi (raw)
        session_dir = pathlib.Path(single_session["session_dir"])
        session_path = find_full_path(get_miniscope_root_data_dir(), session_dir)
        recording_filepaths = [
            file_path.as_posix() for file_path in session_path.glob("*.avi")
        ]
        if not recording_filepaths:
            raise FileNotFoundError(f"No .avi files found in " f"{session_path}")

        # Read Miniscope DAQ *.json file
        for metadata_filepath in session_path.glob("metaData.json"):
            try:
                recording_time = datetime.fromtimestamp(
                    metadata_filepath.stat().st_ctime
                )
                with open(metadata_filepath) as json_file:
                    recording_metadata = json.load(json_file)
                acquisition_hardware = recursive_search(
                    "deviceType", recording_metadata
                )
                break
            except OSError:
                logger.warning(
                    f"Could not find `deviceType` in Miniscope-DAQ json: "
                    f"{metadata_filepath}"
                )
                continue

        session_key = dict(
            subject=single_session["subject"], session_datetime=recording_time
        )
        if session_key not in session.Session():
            hardware_list.append(
                dict(device=acquisition_hardware, modality="Miniscope")
            )

            session_list.append(session_key)

            session_dir_list.append(
                dict(**session_key, session_dir=session_dir.as_posix())
            )

            recording_list.append(
                dict(
                    **session_key,
                    recording_id=0,  # Assumes 1 recording per sess
                    device=acquisition_hardware,
                    acq_software=acq_software,
                )
            )

    insert_string = "---- Inserting %s entry(s) into %s ----"  # defer number/table name

    prev_len = len(Device())
    Device.insert(hardware_list, skip_duplicates=True)  # expect duplicates for Device
    added_len = len(Device()) - prev_len
    logger.info(insert_string % (added_len, "reference.Device"))

    prev_len = len(session.Session())
    session.Session.insert(session_list, skip_duplicates=skip_duplicates)
    session.SessionDirectory.insert(session_dir_list, skip_duplicates=skip_duplicates)
    added_len = len(session.Session()) - prev_len
    logger.info(insert_string % (added_len, "session.Session"))

    prev_len = len(miniscope.Recording())
    miniscope.Recording.insert(recording_list, skip_duplicates=skip_duplicates)
    added_len = len(miniscope.Recording()) - prev_len
    logger.info(insert_string % (added_len, "miniscope.Recording"))

    logger.info("---- Successfully completed ingest_sessions ----")

    if not verbose:
        logger.setLevel(prev_loglevel)


def ingest_events(
    recording_csv_path: str = "./user_data/behavior_recordings.csv",
    block_csv_path: str = "./user_data/blocks.csv",
    trial_csv_path: str = "./user_data/trials.csv",
    event_csv_path: str = "./user_data/events.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest each level of experiment hierarchy for element-trial

    Ingestion hierarchy includes:
        recording, block (i.e., phases of trials), trials (repeated units),
        events (optionally 0-duration occurrences within trial).

    Note: This ingestion function is duplicated across wf-array-ephys and wf-calcium-imaging

    Args:
        recording_csv_path (str, optional): Relative path to recording csv.
            Defaults to "./user_data/behavior_recordings.csv".
        block_csv_path (str, optional): Relative path to block csv.
            Defaults to "./user_data/blocks.csv".
        trial_csv_path (str, optional): Relative path to trial csv.
            Defaults to "./user_data/trials.csv".
        event_csv_path (str, optional): Relative path to event csv.
            Defaults to "./user_data/events.csv".
        skip_duplicates (bool, optional): See DataJoint `insert` function. Default True.
        verbose (bool, optional): Print number inserted (i.e., table length change).
            Defaults to True.
    """
    csvs = [
        recording_csv_path,
        recording_csv_path,
        block_csv_path,
        block_csv_path,
        trial_csv_path,
        trial_csv_path,
        trial_csv_path,
        trial_csv_path,
        event_csv_path,
        event_csv_path,
        event_csv_path,
    ]
    tables = [
        event.BehaviorRecording(),
        event.BehaviorRecording.File(),
        trial.Block(),
        trial.Block.Attribute(),
        trial.TrialType(),
        trial.Trial(),
        trial.Trial.Attribute(),
        trial.BlockTrial(),
        event.EventType(),
        event.Event(),
        trial.TrialEvent(),
    ]

    ingest_csv_to_table(
        csvs,
        tables,
        skip_duplicates=skip_duplicates,
        verbose=verbose,
        allow_direct_insert=True,
    )
    # Allow direct insert required bc element-trial has Imported that should be Manual


def ingest_alignment(
    alignment_csv_path: str = "./user_data/alignments.csv",
    skip_duplicates: bool = True,
    verbose: bool = True,
):
    """Ingest event alignment data from local CSVs

    Note: This is duplicated across wf-array-ephys and wf-calcium-imaging

    Args:
        alignment_csv_path (str, optional): Relative path to event alignment csv.
            Defaults to "./user_data/alignments.csv".
        skip_duplicates (bool, optional): See DataJoint `insert` function. Default True.
        verbose (bool, optional): Print number inserted (i.e., table length change).
            Defaults to True.
    """

    csvs = [alignment_csv_path]
    tables = [event.AlignmentEvent()]

    ingest_csv_to_table(csvs, tables, skip_duplicates=skip_duplicates, verbose=verbose)


def recursive_search(key, dictionary) -> any:
    """Return value for key in a nested dictionary

    Search through a nested dictionary for a key and returns its value.  If there are
    more than one key with the same name at different depths, the algorithm returns the
    value of the least nested key.

    Args:
        key (str): Key used to search through a nested dictionary
        dictionary (dict): Nested dictionary

    Returns:
        value (any): value of the input argument `key`
    """
    if key in dictionary:
        return dictionary[key]
    for value in dictionary.values():
        if isinstance(value, dict):
            a = recursive_search(key, value)
            if a is not None:
                return a
    return None


if __name__ == "__main__":
    ingest_subjects()
    ingest_sessions()
    ingest_events()
    ingest_alignment()
