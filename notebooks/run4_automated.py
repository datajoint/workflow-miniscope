# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
# ---

# or with the `ingest` method and accompanying `csv` files.

# # Automated workflow
# ### Method for inserting entries
#
# Modify `user_data/subjects.csv` and `user_data/sessions.csv`, and run the following commands

from workflow_miniscope.ingest import ingest_subjects, ingest_sessions
ingest_subjects()
ingest_sessions()

# +
import pathlib
from workflow_miniscope.paths import get_imaging_root_data_dir

root_dir = pathlib.Path(get_imaging_root_data_dir())

for scan_key in (scan.Scan & scan.ScanInfo - imaging.ProcessingTask).fetch('KEY'):
    scan_file = root_dir / (scan.ScanInfo.ScanFile & scan_key).fetch('file_path')[0]
    recording_dir = scan_file.parent

    miniscope_analysis_dir = recording_dir / 'miniscope_analysis'
    if miniscope_analysis_dir.exists():
        imaging.ProcessingTask.insert1({**scan_key,
                                        'paramset_idx': 0,
                                        'processing_output_dir': miniscope_analysis_dir.as_posix()})
# -



# + To this end, we make use of a convenient function `imaging.Curation().create1_from_processing_task()`

for key in (imaging.ProcessingTask - imaging.Curation).fetch('KEY'):
    imaging.Curation().create1_from_processing_task(key)

# ### Method for populating tables

from workflow_miniscope.populate import populate
populate(display_progress=False)
