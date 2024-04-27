from typing import Union, List

from .point_sequence_plotter import TemporalPointSequencePlotter
from .. import TPointSeq
from ..main import TPointSeqSet


class TemporalPointSequenceSetPlotter:
    """
    Plotter for :class:`TPointSeqSet` and lists of :class:`TPointSeq`.
    """

    @staticmethod
    def plot_xy(sequence_set: Union[TPointSeqSet, List[TPointSeq]], *args, **kwargs):
        """
        Plot a TPointSeqSet or a list of TPointSeq on the given axes. Every sequence in the set will be plotted with the
        same color.

        Params:
            sequence_set: The :class:`TPointSeqSet` or list of :class:`TPointSeq` to plot.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List of lists with the plotted elements of each sequence.

        See Also:
            :func:`~pymeos.plotters.point_sequence_plotter.TemporalPointSequencePlotter.plot_xy`,
            :func:`~pymeos.plotters.point_sequence_plotter.TemporalPointSequencePlotter.plot_sequences_xy`
        """
        seqs = (
            sequence_set.sequences()
            if isinstance(sequence_set, TPointSeqSet)
            else sequence_set
        )
        plots = [TemporalPointSequencePlotter.plot_xy(seqs[0], *args, **kwargs)]
        if "color" not in kwargs:
            kwargs["color"] = plots[0][0][0].get_color()
        kwargs.pop("label", None)
        for seq in seqs[1:]:
            plots.append(TemporalPointSequencePlotter.plot_xy(seq, *args, **kwargs))
        return plots
