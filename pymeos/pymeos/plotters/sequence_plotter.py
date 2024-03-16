from functools import partial
from typing import Union, List

import matplotlib.pyplot as plt

from ..temporal import TSequence, TInterpolation, TInstant


class TemporalSequencePlotter:
    """
    Plotter for :class:`TSequence` and lists of :class:`TInstant`.
    """

    @staticmethod
    def plot(
        sequence: Union[TSequence, List[TInstant]],
        *args,
        axes=None,
        show_markers=True,
        show_grid=True,
        **kwargs,
    ):
        """
        Plot a :class:`TSequence` or a list of :class:`TInstant` on the given axes. The actual plot function is chosen
        based on the interpolation of the sequence.

        Params:
            sequence: The :class:`TSequence` or list of :class:`TInstant` to plot.
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
        if isinstance(sequence, list):
            plot_func = base.scatter
            show_markers = False
        elif sequence.interpolation() == TInterpolation.LINEAR:
            plot_func = base.plot
        elif sequence.interpolation() == TInterpolation.STEPWISE:
            plot_func = partial(base.step, where="post")
        else:
            plot_func = base.scatter
            show_markers = False

        ins = sequence.instants() if isinstance(sequence, TSequence) else sequence
        x = [i.timestamp() for i in ins]
        y = [i.value() for i in ins]

        base.set_axisbelow(True)

        if show_grid:
            base.grid(zorder=0.5)
        plots = [plot_func(x, y, *args, **kwargs)]

        if show_markers:
            color = plots[0][0].get_color()
            plots.append(
                base.scatter(
                    x[0],
                    y[0],
                    s=40,
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
                    s=40,
                    marker="o",
                    facecolors=color if sequence.upper_inc() else "none",
                    edgecolors=color,
                    zorder=2 if sequence.upper_inc() else 3,
                )
            )

        if isinstance(y[0], bool):
            plt.yticks([1.0, 0.0], ["True", "False"])
            plt.ylim(-0.25, 1.25)

        base.tick_params(axis="x", rotation=45)

        return plots

    @staticmethod
    def plot_sequences(sequences: List[TSequence], *args, **kwargs):
        """
        Plot a list of :class:`TSequence` on the given axes. Every sequence will be plotted in a different color.

        Params:
            sequences: The list of :class:`TSequence` to plot.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List of lists with the plotted elements of each sequence.

        See Also:
            :func:`~pymeos.plotters.sequence_plotter.TemporalSequencePlotter.plot`,
            :meth:`~pymeos.plotters.sequenceset_plotter.TemporalSequenceSetPlotter.plot`
        """
        plots = []
        for seq in sequences:
            plots.append(TemporalSequencePlotter.plot(seq, *args, **kwargs))
        return plots
