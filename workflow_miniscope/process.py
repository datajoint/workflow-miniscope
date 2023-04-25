import logging
from contextlib import nullcontext

from datajoint.utils import to_camel_case
from element_interface.utils import QuietStdOut

from workflow_miniscope.pipeline import miniscope

logger = logging.getLogger("datajoint")


def run(
    verbose: bool = True,
    display_progress: bool = True,
    reserve_jobs: bool = False,
    suppress_errors: bool = False,
):
    """Run all `make` methods from Element Miniscope

    Args:
        verbose (bool, optional): Print which table is in being populated. Default True.
        display_progress (bool, optional): tqdm progress bar. Defaults to True.
        reserve_jobs (bool, optional): Reserves job to populate in asynchronous fashion.
            Defaults to False.
        suppress_errors (bool, optional): Suppress errors that would halt execution.
            Defaults to False.
    """
    populate_settings = {
        "display_progress": display_progress,
        "reserve_jobs": reserve_jobs,
        "suppress_errors": suppress_errors,
    }

    tables = [
        miniscope.RecordingInfo(),
        miniscope.Processing(),
        miniscope.MotionCorrection(),
        miniscope.Segmentation(),
        miniscope.Fluorescence(),
        miniscope.Activity(),
    ]

    with nullcontext() if verbose else QuietStdOut():
        for table in tables:
            logger.info(f"---- Populating {to_camel_case(table.table_name)} ----")
            table.populate(**populate_settings)
        logger.info("---- Successfully completed miniscope/populate.py ----")


if __name__ == "__main__":
    run()
