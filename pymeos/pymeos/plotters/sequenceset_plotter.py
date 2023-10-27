from typing import List, Union

from .sequence_plotter import TemporalSequencePlotter
from .. import TSequence
from ..temporal import TSequenceSet


class TemporalSequenceSetPlotter:
    """
    Plotter for :class:`TSequenceSet` and lists of :class:`TSequence`.
    """

    @staticmethod
    def plot(sequence_set: Union[TSequenceSet, List[TSequence]], *args, **kwargs):
        """
        Plot a :class:`TSequenceSet` or a list of :class:`TSequence` on the given axes. Every sequence in the set will be
        plotted with the same color.

        Params:
            sequence_set: The :class:`TSequenceSet` or list of :class:`TSequence` to plot.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.

        See Also:
            :func:`~pymeos.plotters.sequence_plotter.TemporalSequencePlotter.plot`

        """
        seqs = (
            sequence_set.sequences()
            if isinstance(sequence_set, TSequenceSet)
            else sequence_set
        )
        plots = [TemporalSequencePlotter.plot(seqs[0], *args, **kwargs)]
        if "color" not in kwargs:
            pl = plots[0]
            while isinstance(pl, list):
                pl = pl[0]
            kwargs["color"] = pl.get_color()
        kwargs.pop("label", None)
        for seq in seqs[1:]:
            plots.append(TemporalSequencePlotter.plot(seq, *args, **kwargs))
        return plots
