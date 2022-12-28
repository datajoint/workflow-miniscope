import warnings

from workflow_miniscope.pipeline import miniscope

warnings.filterwarnings("ignore")


def run(display_progress=True, reserve_jobs=False, suppress_errors=False, verbose=True):
    """Execute all populate commands in Element

    Args:
        display_progress (bool, optional): See DataJoint `populate`. Defaults to True.
        reserve_jobs (bool, optional): See DataJoint `populate`. Defaults to False.
        suppress_errors (bool, optional): See DataJoint `populate`. Defaults to False.
        verbose (bool, optional): Print start/end statements. Defaults to True.
    """

    populate_settings = {
        "display_progress": display_progress,
        "reserve_jobs": reserve_jobs,
        "suppress_errors": suppress_errors,
    }

    if verbose:
        print("\n---- Populate imported and computed tables ----")

    miniscope.RecordingInfo.populate(**populate_settings)

    miniscope.Processing.populate(**populate_settings)

    miniscope.MotionCorrection.populate(**populate_settings)

    miniscope.Segmentation.populate(**populate_settings)

    miniscope.Fluorescence.populate(**populate_settings)

    miniscope.Activity.populate(**populate_settings)

    if verbose:
        print("\n---- Successfully completed workflow_miniscope/populate.py ----")


if __name__ == "__main__":
    run()
