from workflow_miniscope.pipeline import miniscope
import warnings

warnings.filterwarnings('ignore')


def run(display_progress=True):

    populate_settings = {'display_progress': display_progress,
                         'reserve_jobs': False,
                         'suppress_errors': False}

    print('\n---- Populate imported and computed tables ----')

    miniscope.RecordingInfo.populate(**populate_settings)

    miniscope.Processing.populate(**populate_settings)

    miniscope.MotionCorrection.populate(**populate_settings)

    miniscope.Segmentation.populate(**populate_settings)

    miniscope.Fluorescence.populate(**populate_settings)

    miniscope.Activity.populate(**populate_settings)

    print('\n---- Successfully completed workflow_miniscope/populate_all.py ----')


if __name__ == '__main__':
    run()