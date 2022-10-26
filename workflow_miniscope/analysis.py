import matplotlib.pyplot as plt
import datajoint as dj
import numpy as np

from workflow_miniscope.pipeline import db_prefix, session, miniscope, trial


schema = dj.schema(db_prefix + "analysis")


@schema
class ActivityAlignmentCondition(dj.Manual):
    """Alignment activity table

    Attributes:
        miniscope.Activity (foreign key)
        event.AlignmentEvent (foreign key)
        trial_condition: varchar(128) # user-friendly name of condition
        condition_description ( varchar(1000), nullable): condition description
        bin_size (float, optional): Bin-size (in second) used to compute the PSTH
            Default 0.04
    """

    definition = """
    -> miniscope.Activity
    -> event.AlignmentEvent
    trial_condition: varchar(128) # user-friendly name of condition
    ---
    condition_description='': varchar(1000)
    bin_size=0.04: float # bin-size (in second) used to compute the PSTH
    """

    class Trial(dj.Part):
        definition = """  # Trials (or subset) to compute event-aligned activity
        -> master
        -> trial.Trial
        """


@schema
class ActivityAlignment(dj.Computed):
    """Computed table for alignment activity

    Attributes:
        ActivityAlignmentCondition (foreign key)
        aligned_timestamps (longblob)
    """

    definition = """
    -> ActivityAlignmentCondition
    ---
    aligned_timestamps: longblob
    """

    class AlignedTrialActivity(dj.Part):
        """Calcium activity aligned to the event time within the designated window

        Attributes:
            miniscope.Activity.Trace (foreign key)
            ActivityAlignmentCondition.Trial (foreign key)
            aligned_trace (longblob): (s) Calcium activity aligned to the event time
        """

        definition = """
        -> master
        -> miniscope.Activity.Trace
        -> ActivityAlignmentCondition.Trial
        ---
        aligned_trace: longblob  # (s) Calcium activity aligned to the event time
        """

    def make(self, key):
        """Populate ActivityAlignment and AlignedTrialActivity

        Args:
            key (dict): Dict uniquely identifying one ActivityAlignmentCondition
        """
        sess_time, rec_time, nframes, frame_rate = (
            miniscope.RecordingInfo * session.Session & key
        ).fetch1("session_datetime", "recording_datetime", "nframes", "fps")

        # Estimation of frame timestamps with respect to the session-start
        # (to be replaced by timestamps retrieved from some synchronization routine)
        rec_start = (rec_time - sess_time).total_seconds() if rec_time else 0
        frame_timestamps = np.arange(nframes) / frame_rate + rec_start

        trialized_event_times = trial.get_trialized_alignment_event_times(
            key, trial.Trial & (ActivityAlignmentCondition.Trial & key)
        )

        min_limit = (trialized_event_times.event - trialized_event_times.start).max()
        max_limit = (trialized_event_times.end - trialized_event_times.event).max()

        aligned_timestamps = np.arange(-min_limit, max_limit, 1 / frame_rate)
        nsamples = len(aligned_timestamps)

        trace_keys, activity_traces = (miniscope.Activity.Trace & key).fetch(
            "KEY", "activity_trace", order_by="mask_id"
        )
        activity_traces = np.vstack(activity_traces)

        aligned_trial_activities = []
        for _, r in trialized_event_times.iterrows():
            if r.event is None or np.isnan(r.event):
                continue
            alignment_start_idx = int((r.event - min_limit) * frame_rate)
            roi_aligned_activities = activity_traces[
                :, alignment_start_idx : (alignment_start_idx + nsamples)
            ]
            if roi_aligned_activities.shape[-1] != nsamples:
                shape_diff = nsamples - roi_aligned_activities.shape[-1]
                roi_aligned_activities = np.pad(
                    roi_aligned_activities,
                    ((0, 0), (0, shape_diff)),
                    mode="constant",
                    constant_values=np.nan,
                )

            aligned_trial_activities.extend(
                [
                    {**key, **r.trial_key, **trace_key, "aligned_trace": aligned_trace}
                    for trace_key, aligned_trace in zip(
                        trace_keys, roi_aligned_activities
                    )
                ]
            )

        self.insert1({**key, "aligned_timestamps": aligned_timestamps})
        self.AlignedTrialActivity.insert(aligned_trial_activities)

    def plot_aligned_activities(
        self, key: dict, roi, axs: tuple = None, title: str = None
    ) -> plt.figure.Figure:
        """Plot event-aligned and trial-averaged calcium activities

        Activities including: dF/F, neuropil-corrected dF/F, Calcium events, etc.

        Args:
            key (dict): key of ActivityAlignment master table
            roi (_type_): miniscope segmentation mask
            axs (tuple, optional): Definition of axes for plot.
                Default is plt.subplots(2, 1, figsize=(12, 8))
            title (str, optional): Optional title label. Defaults to None.

        Returns:
            fig (matplotlib.figure.Figure): Plot event-aligned and trial-averaged
                calcium activities
        """

        fig = None
        if axs is None:
            fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 8))
        else:
            ax0, ax1 = axs

        aligned_timestamps = (self & key).fetch1("aligned_timestamps")
        trial_ids, aligned_spikes = (
            self.AlignedTrialActivity & key & {"mask_id": roi}
        ).fetch("trial_id", "aligned_trace", order_by="trial_id")

        aligned_spikes = np.vstack(aligned_spikes)

        ax0.imshow(
            aligned_spikes,
            cmap="inferno",
            interpolation="nearest",
            aspect="auto",
            extent=(
                aligned_timestamps[0],
                aligned_timestamps[-1],
                0,
                aligned_spikes.shape[0],
            ),
        )
        ax0.axvline(x=0, linestyle="--", color="white")
        ax0.set_axis_off()

        ax1.plot(aligned_timestamps, np.nanmean(aligned_spikes, axis=0))
        ax1.axvline(x=0, linestyle="--", color="black")
        ax1.set_xlabel("Time (s)")
        ax1.set_xlim(aligned_timestamps[0], aligned_timestamps[-1])

        if title:
            plt.suptitle(title)

        return fig
