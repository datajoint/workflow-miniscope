import pathlib
import csv
from datetime import datetime
import json

from .pipeline import subject, session, Equipment, miniscope
from .paths import get_miniscope_root_data_dir
from element_interface.utils import find_full_path, recursive_search

def ingest_subjects(subject_csv_path='./user_data/subjects.csv'):
    print('\n-------------- Insert new "Subject" --------------')
    with open(subject_csv_path, newline= '') as f:
        input_subjects = list(csv.DictReader(f, delimiter=','))

    print(f'\n---- Insert {len(input_subjects)} entry(s) into subject.Subject ----')
    subject.Subject.insert(input_subjects, skip_duplicates=True)

    print('\n---- Successfully completed ingest_subjects ----')


def ingest_sessions(session_csv_path='./user_data/sessions.csv'):

    print('\n---- Insert new `Session` and `Recording` ----')
    with open(session_csv_path, newline='') as f:
        input_sessions = list(csv.DictReader(f, delimiter=','))

    session_list, session_dir_list, recording_list, hardware_list = [], [], [], []

    for single_session in input_sessions:
        acquisition_software = single_session['acquisition_software']
        if acquisition_software not in ['Miniscope-DAQ-V3', 'Miniscope-DAQ-V4']:
            raise NotImplementedError(f'Not implemented for acquisition software of '
                                      f'type {acquisition_software}.')

        # Folder structure: root / subject / session / .avi (raw)
        session_dir = pathlib.Path(single_session['session_dir'])
        session_path = find_full_path(get_miniscope_root_data_dir(),
                                      session_dir)
        recording_filepaths = [file_path.as_posix() for file_path 
                                            in session_path.glob('*.avi')]
        if not recording_filepaths:
            raise FileNotFoundError(f'No .avi files found in '
                                    f'{session_path}')

        # Read Miniscope DAQ *.json file
        for metadata_filepath in session_path.glob('metaData.json'):
            try:
                recording_time = datetime.fromtimestamp(
                                                    metadata_filepath.stat().st_ctime)
                with open(metadata_filepath) as json_file:
                    recording_metadata = json.load(json_file)
                acquisition_hardware = recursive_search('deviceType', 
                                                        recording_metadata)
                break
            except OSError:
                print(f'Could not find `deviceType` in Miniscope-DAQ json: '
                      f'{metadata_filepath}')
                continue

        session_key = dict(subject=single_session['subject'], 
                           session_datetime=recording_time)
        if session_key not in session.Session():
            hardware_list.append(dict(acquisition_hardware=acquisition_hardware))

            session_list.append(session_key)

            session_dir_list.append(dict(**session_key, 
                                         session_dir=session_dir.as_posix()))

            recording_list.append(dict(**session_key, 
                                   recording_id=0, # Assumes one recording per session
                                   acquisition_hardware=acquisition_hardware, 
                                   acquisition_software=acquisition_software,
                                   recording_directory=session_dir.as_posix()))

    print(f'\n---- Insert {len(set(val for dic in hardware_list for val in dic.values()))} entry(s) into lab.Equipment ----')
    Equipment.insert(hardware_list, skip_duplicates=True)

    print(f'\n---- Insert {len(session_list)} entry(s) into session.Session ----')
    session.Session.insert(session_list)
    session.SessionDirectory.insert(session_dir_list)

    print(f'\n---- Insert {len(recording_list)} entry(s) into miniscope.Recording ----')
    miniscope.Recording.insert(recording_list)

    print('\n---- Successfully completed ingest_sessions ----')


if __name__ == '__main__':
    ingest_subjects()
    ingest_sessions()
