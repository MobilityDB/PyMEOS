from functools import partial
from typing import Union, List

import matplotlib.pyplot as plt

from ..temporal import TSequence, TInterpolation, TInstant


class TemporalSequencePlotter:

    @staticmethod
    def plot(sequence: Union[TSequence, List[TInstant]], *args, axes=None, **kwargs):
        base = axes or plt.gca()
        if isinstance(sequence, list):
            plot_func = base.scatter
        elif sequence.interpolation == TInterpolation.LINEAR:
            plot_func = base.plot
        elif sequence.interpolation == TInterpolation.STEPWISE:
            plot_func = partial(base.step, where='post')
        else:
            plot_func = base.scatter

        ins = sequence.instants if isinstance(sequence, TSequence) else sequence
        x = [i.timestamp for i in ins]
        y = [i.value() for i in ins]

        base.set_axisbelow(True)

        base.grid(zorder=0.5)
        plot = plot_func(x, y, *args, **kwargs)

        if sequence.interpolation != TInterpolation.DISCRETE:
            color = plot[0].get_color()
            base.scatter(x[0], y[0], s=40, marker='o', facecolors=color if sequence.lower_inc else 'none',
                         edgecolors=color, zorder=2 if sequence.upper_inc else 3)
            base.scatter(x[-1], y[-1], s=40, marker='o', facecolors=color if sequence.upper_inc else 'none',
                         edgecolors=color, zorder=2 if sequence.upper_inc else 3)

        if isinstance(y[0], bool):
            plt.yticks([1.0, 0.0], ['True', 'False'])
            plt.ylim(-0.25, 1.25)

        base.tick_params(axis="x", rotation=45)

        return plot
