from functools import partial
from typing import Union, List

import matplotlib.pyplot as plt

from ..temporal import TSequence, TInterpolation, TInstant


class TemporalSequencePlotter:

    @classmethod
    def plot(cls, sequence: Union[TSequence, List[TInstant]], *args, axes=None, **kwargs):
        base = axes or plt.gca()
        plot_func = None
        if sequence.interpolation == TInterpolation.LINEAR:
            plot_func = base.plot
        elif sequence.interpolation == TInterpolation.STEPWISE:
            plot_func = partial(base.step, where='post')
        elif sequence.interpolation == TInterpolation.DISCRETE:
            plot_func = base.scatter

        ins = sequence.instants if isinstance(sequence, TSequence) else sequence
        x = [i.timestamp for i in ins]
        y = [i.value for i in ins]

        base.set_axisbelow(True)

        base.grid(zorder=0.5)
        plot = plot_func(x, y, *args, **kwargs)

        if sequence.interpolation != TInterpolation.DISCRETE:
            color = plot[0].get_color()
            base.scatter(x[0], y[0], s=80, marker='o', facecolors=color if sequence.lower_inc else 'none',
                         edgecolors=color)
            base.scatter(x[-1], y[-1], s=80, marker='o', facecolors=color if sequence.upper_inc else 'none',
                         edgecolors=color)

        if isinstance(y[0], bool):
            plt.yticks([1.0, 0.0], ['True', 'False'])
            plt.ylim(-0.25, 1.25)

        plt.xticks(rotation=45)

        return plot
