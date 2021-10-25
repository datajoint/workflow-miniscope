from workflow_miniscope.pipeline import *

populate_settings = {'display_progress': True}

# Subject ----------------------------------------------------------------------
subject.Subject.insert1(dict(subject='LO012', 
                             sex='F', 
                             subject_birth_date='2020-01-01', 
                             subject_description=''))

# Session ----------------------------------------------------------------------
Equipment.insert1(dict(scanner='UCLA Miniscope'))

session_key = dict(subject='LO012', 
                   session_datetime='2021-08-25 23:45:44')

session.Session.insert1(session_key)

session.SessionDirectory.insert1(dict(**session_key, 
                                      session_dir='LO012/20210825_234544'))

recording_key = dict(session_key,
                     recording_id=0)

miniscope.Recording.insert1(dict(**recording_key,
                                 scanner='UCLA Miniscope', 
                                 acquisition_software='Miniscope-DAQ-V4',
                                 recording_directory='LO012/20210825_234544/miniscope',
                                 recording_notes=''))

miniscope.RecordingInfo.populate(**populate_settings)

# Motion Correction ------------------------------------------------------------
# motion_correction_params_caiman = {}

# miniscope.MotionCorrectionParamSet.insert_new_params(
#     motion_correction_method='caiman', 
#     motion_correction_paramset_id=0, 
#     motion_correction_paramset_desc='Miniscope analysis with CaImAn using default parameters',
#     motion_correction_params=motion_correction_params_caiman)

# miniscope.MotionCorrectionTask.insert1(dict(**recording_key, 
#                                             motion_correction_task_id=0,
#                                             motion_correction_paramset_id=0,
#                                             motion_correction_output_dir='LO012/20210825_234544/miniscope/caiman',
#                                             motion_correction_task_mode='load'))

# miniscope.MotionCorrection.populate(**populate_settings)

# Segmentation -----------------------------------------------------------------
# miniscope.Segmentation.populate(**populate_settings)

# miniscope.MaskClassification.populate(**populate_settings)

# miniscope.Fluorescence.populate(**populate_settings)

# Deconvolution ----------------------------------------------------------------
# miniscope.Activity.populate(**populate_settings)

