from typing import Union, List

import matplotlib.pyplot as plt

from ..main import TPointSeq, TPointInst
from ..temporal import TInterpolation


class TemporalPointSequencePlotter:

    @staticmethod
    def plot_xy(sequence: Union[TPointSeq, List[TPointInst]], *args, axes=None, show_markers=True, show_grid=True,
                **kwargs):
        base = axes or plt.gca()
        linear = False
        if isinstance(sequence, list):
            plot_func = base.scatter
        elif sequence.interpolation == TInterpolation.LINEAR:
            plot_func = base.plot
            linear = True
        else:
            plot_func = base.scatter

        ins = sequence.instants() if isinstance(sequence, TPointSeq) else sequence
        x = [i.x().value() for i in ins]
        y = [i.y().value() for i in ins]

        base.set_axisbelow(True)

        if show_grid:
            base.grid(zorder=0.5)
        plot = plot_func(x, y, *args, **kwargs)

        if linear and show_markers:
            color = plot[0].get_color()
            base.scatter(x[0], y[0], s=80, marker='o', facecolors=color if sequence.lower_inc else 'none',
                         edgecolors=color, zorder=2 if sequence.lower_inc else 3)
            base.scatter(x[-1], y[-1], s=80, marker='o', facecolors=color if sequence.upper_inc else 'none',
                         edgecolors=color, zorder=2 if sequence.upper_inc else 3)

        base.tick_params(axis="x", rotation=45)

        return plot

    @staticmethod
    def plot_sequences_xy(sequences: List[TPointSeq], *args, **kwargs):
        plots = []
        for seq in sequences:
            plots.append(TemporalPointSequencePlotter.plot_xy(seq, *args, **kwargs))
        return plots
