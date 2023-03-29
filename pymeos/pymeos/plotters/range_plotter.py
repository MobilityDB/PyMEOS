from typing import Union

from matplotlib import pyplot as plt
from spans import floatrange, intrange


class RangePlotter:
    """
    Plotter for :class:`floatrange` and :class:`intrange` objects.
    """

    @staticmethod
    def plot_range(range: Union[floatrange, intrange], *args, axes=None, **kwargs):
        """
        Plot a :class:`floatrange` or :class:`intrange` on the given axes.

        Params:
            range: The :class:`floatrange` or :class:`intrange` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        ll = base.axhline(range.lower, *args, linestyle='-' if range.lower_inc else '--', **kwargs)
        kwargs.pop('label', None)
        ul = base.axhline(range.upper, *args, linestyle='-' if range.upper_inc else '--', **kwargs)
        s = base.axhspan(range.lower, range.upper, *args, alpha=0.3, **kwargs)
        return [ll, ul, s]
