from datetime import datetime
from typing import Union

from matplotlib import pyplot as plt

from ..collections import TsTzSet, TsTzSpan, TsTzSpanSet
from ..collections.time.dateset import DateSet


class TimePlotter:
    """
    Plotter for :class:`Time` objects.
    """

    @staticmethod
    def plot_timestamp(timestamp: datetime, *args, axes=None, **kwargs):
        """
        Plot a :class:`datetime` on the given axes as a vertical line.

        Params:
            timestamp: The :class:`datetime` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        return base.axvline(timestamp, *args, **kwargs)

    @staticmethod
    def plot_tstzset(tstzset: TsTzSet, *args, axes=None, **kwargs):
        """
        Plot a :class:`TsTzSet` on the given axes as a vertical line for each timestamp.

        Params:
            tstzset: The :class:`TsTzSet` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        stamps = tstzset.elements()
        plot = base.axvline(stamps[0], *args, **kwargs)
        kwargs.pop("label", None)
        plots = [plot]
        for stamp in stamps[1:]:
            plots.append(base.axvline(stamp, *args, color=plot.get_color(), **kwargs))
        return plots

    @staticmethod
    def plot_tstzspan(tstzspan: TsTzSpan, *args, axes=None, **kwargs):
        """
        Plot a :class:`TsTzSpan` on the given axes as two vertical lines filled in between. The lines will be
        dashed if the tstzspan is open.

        Params:
            tstzspan: The :class:`TsTzSpan` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        ll = base.axvline(
            tstzspan.lower(),
            *args,
            linestyle="-" if tstzspan.lower_inc() else "--",
            **kwargs,
        )
        kwargs.pop("label", None)
        ul = base.axvline(
            tstzspan.upper(),
            *args,
            linestyle="-" if tstzspan.upper_inc() else "--",
            **kwargs,
        )
        s = base.axvspan(tstzspan.lower(), tstzspan.upper(), *args, alpha=0.3, **kwargs)
        return [ll, ul, s]

    @staticmethod
    def plot_tstzspanset(tstzspanset: TsTzSpanSet, *args, axes=None, **kwargs):
        """
        Plot a :class:`TsTzSpanSet` on the given axes as a vertical line for each timestamp.

        Params:
            tstzspanset: The :class:`TsTzSpanSet` to plot.
            *args: Additional arguments to pass to the plot function.
            axes: The axes to plot on. If None, the current axes are used.

        Returns:
            List with the plotted elements.

        See also:
            :func:`~pymeos.plotters.time_plotter.TimePlotter.plot_tstzspan`
        """
        tstzspans = tstzspanset.tstzspans()
        line = TimePlotter.plot_tstzspan(tstzspans[0], *args, axes=axes, **kwargs)
        kwargs.pop("label", None)
        lines = [line]
        if "color" not in kwargs:
            kwargs["color"] = line[0].get_color()
        for p in tstzspans[1:]:
            lines.append(TimePlotter.plot_tstzspan(p, *args, axes=axes, **kwargs))
        return lines
