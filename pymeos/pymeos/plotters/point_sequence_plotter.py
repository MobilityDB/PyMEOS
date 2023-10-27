from typing import Union, List

import matplotlib.pyplot as plt

from ..main import TPointSeq, TPointInst
from ..temporal import TInterpolation


class TemporalPointSequencePlotter:
    """
    Plotter for :class:`TPointSeq` and lists of :class:`TPointInst`.
    """

    @staticmethod
    def plot_xy(
        sequence: Union[TPointSeq, List[TPointInst]],
        *args,
        axes=None,
        show_markers=True,
        show_grid=True,
        **kwargs,
    ):
        """
        Plot a TPointSeq or a list of TPointInst on the given axes. The actual plot function is chosen
        based on the interpolation of the sequence.

        Params:
            sequence: The :class:`TPointSeq` or list of :class:`TPointInst` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            show_markers: Whether to show markers at the start and end of the sequence. The marker will be filled if the
            sequence is inclusive at that end, and empty otherwise.
            show_grid: Whether to show a grid.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        linear = False
        if isinstance(sequence, list):
            plot_func = base.scatter
        elif sequence.interpolation() == TInterpolation.LINEAR:
            plot_func = base.plot
            linear = True
        else:
            plot_func = base.scatter

        ins: list[TPointInst] = (
            sequence.instants() if isinstance(sequence, TPointSeq) else sequence
        )
        x = [i.x().value() for i in ins]
        y = [i.y().value() for i in ins]

        base.set_axisbelow(True)

        if show_grid:
            base.grid(zorder=0.5)
        plots = [plot_func(x, y, *args, **kwargs)]

        if linear and show_markers:
            color = plots[0][0].get_color()
            plots.append(
                base.scatter(
                    x[0],
                    y[0],
                    s=80,
                    marker="o",
                    facecolors=color if sequence.lower_inc() else "none",
                    edgecolors=color,
                    zorder=2 if sequence.lower_inc() else 3,
                )
            )
            plots.append(
                base.scatter(
                    x[-1],
                    y[-1],
                    s=80,
                    marker="o",
                    facecolors=color if sequence.upper_inc() else "none",
                    edgecolors=color,
                    zorder=2 if sequence.upper_inc() else 3,
                )
            )

        base.tick_params(axis="x", rotation=45)

        return plots

    @staticmethod
    def plot_sequences_xy(sequences: List[TPointSeq], *args, **kwargs):
        """
        Plot a list of TPointSeq on the given axes. Every sequence will be plotted in a different color.

        Params:
            sequences: The list of :class:`TPointSeq` to plot.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List of lists with the plotted elements of each sequence.

        See Also:
            :func:`~pymeos.plotters.point_sequence_plotter.TemporalPointSequencePlotter.plot_xy`,
            :meth:`~pymeos.plotters.point_sequenceset_plotter.TemporalPointSequenceSetPlotter.plot_xy`
        """
        plots = []
        for seq in sequences:
            plots.append(TemporalPointSequencePlotter.plot_xy(seq, *args, **kwargs))
        return plots
