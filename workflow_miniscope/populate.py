from workflow_miniscope.pipeline import miniscope
import warnings

warnings.filterwarnings('ignore')


def populate(display_progress=True, reserve_jobs=False, suppress_errors=False,
             verbose=True):

    populate_settings = {'display_progress': display_progress,
                         'reserve_jobs': reserve_jobs,
                         'suppress_errors': suppress_errors}

    if verbose:
        print('\n---- Populate miniscope.ScanInfo ----')
    miniscope.ScanInfo.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.Processing ----')
    miniscope.Processing.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.MotionCorrection ----')
    miniscope.MotionCorrection.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.Segmentation ----')
    miniscope.Segmentation.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.MaskClassification ----')
    miniscope.MaskClassification.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.Fluorescence ----')
    miniscope.Fluorescence.populate(**populate_settings)

    if verbose:
        print('\n---- Populate miniscope.Activity ----')
    miniscope.Activity.populate(**populate_settings)

    if verbose:
        print('\n---- Successfully completed workflow_calcium_imaging/populate.py ----')


if __name__ == '__main__':
    populate()
