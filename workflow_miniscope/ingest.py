import pathlib
import csv
from datetime import datetime

from .pipeline import subject, imaging, scan, session, Equipment
from .paths import get_imaging_root_data_dir


def ingest_subjects(subject_csv_path='./user_data/subjects.csv'):
    # -------------- Insert new "Subject" --------------
    with open(subject_csv_path, newline= '') as f:
        input_subjects = list(csv.DictReader(f, delimiter=','))

    print(f'\n---- Insert {len(input_subjects)} entry(s) into subject.Subject ----')
    subject.Subject.insert(input_subjects, skip_duplicates=True)

    print('\n---- Successfully completed ingest_subjects ----')


def ingest_sessions(session_csv_path='./user_data/sessions.csv'):
    root_data_dir = get_imaging_root_data_dir()

    # ---------- Insert new "Session" and "Scan" ---------
    with open(session_csv_path, newline='') as f:
        input_sessions = list(csv.DictReader(f, delimiter=','))

    # Folder structure: root / subject / session / .avi (raw)
    session_list, session_dir_list, scan_list, scanner_list = [], [], [], []

    for sess in input_sessions:
        sess_dir = pathlib.Path(sess['session_dir'])

        # Search for Miniscope-DAQ-V3 files (in that order)
        for scan_pattern, scan_type, glob_func in zip(['ms*.avi'],
                                                      ['Miniscope-DAQ-V3'],
                                                      [sess_dir.glob]):
            scan_filepaths = [fp.as_posix() for fp in glob_func(scan_pattern)]
            if len(scan_filepaths):
                acq_software = scan_type
                break
        else:
            raise FileNotFoundError(f'Unable to identify scan files from the supported acquisition softwares (Miniscope-DAQ-V3) at: {sess_dir}')

        if acq_software == 'Miniscope-DAQ-V3':
            daq_v3_fp = pathlib.Path(scan_filepaths[0])
            recording_time = datetime.fromtimestamp(daq_v3_fp.stat().st_ctime)
            scanner = 'Miniscope-DAQ-V3'
        else:
            raise NotImplementedError(f'Processing scan from acquisition software of type {acq_software} is not yet implemented')

        session_key = {'subject': sess['subject'], 'session_datetime': recording_time}
        if session_key not in session.Session():
            scanner_list.append({'scanner': scanner})
            session_list.append(session_key)
            scan_list.append({**session_key, 'scan_id': 0, 'scanner': scanner, 'acq_software': acq_software})

            session_dir_list.append({**session_key, 'session_dir': sess_dir.relative_to(root_data_dir).as_posix()})

    print(f'\n---- Insert {len(set(val for dic in scanner_list for val in dic.values()))} entry(s) into experiment.Equipment ----')
    Equipment.insert(scanner_list, skip_duplicates=True)

    print(f'\n---- Insert {len(session_list)} entry(s) into session.Session ----')
    session.Session.insert(session_list)
    session.SessionDirectory.insert(session_dir_list)

    print(f'\n---- Insert {len(scan_list)} entry(s) into scan.Scan ----')
    scan.Scan.insert(scan_list)

    print('\n---- Successfully completed ingest_sessions ----')


if __name__ == '__main__':
    ingest_subjects()
    ingest_sessions()
