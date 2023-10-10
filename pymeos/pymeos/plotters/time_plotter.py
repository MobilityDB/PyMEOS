from datetime import datetime

from matplotlib import pyplot as plt

from ..collections import TimestampSet, Period, PeriodSet


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
    def plot_timestampset(timestampset: TimestampSet, *args, axes=None, **kwargs):
        """
        Plot a :class:`TimestampSet` on the given axes as a vertical line for each timestamp.

        Params:
            timestampset: The :class:`TimestampSet` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        stamps = timestampset.timestamps()
        plot = base.axvline(stamps[0], *args, **kwargs)
        kwargs.pop('label', None)
        plots = [plot]
        for stamp in stamps[1:]:
            plots.append(base.axvline(stamp, *args, color=plot.get_color(), **kwargs))
        return plots

    @staticmethod
    def plot_period(period: Period, *args, axes=None, **kwargs):
        """
        Plot a :class:`Period` on the given axes as two vertical lines filled in between. The lines will be
        dashed if the period is open.

        Params:
            period: The :class:`Period` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        ll = base.axvline(period.lower(), *args, linestyle='-' if period.lower_inc() else '--', **kwargs)
        kwargs.pop('label', None)
        ul = base.axvline(period.upper(), *args, linestyle='-' if period.upper_inc() else '--', **kwargs)
        s = base.axvspan(period.lower(), period.upper(), *args, alpha=0.3, **kwargs)
        return [ll, ul, s]

    @staticmethod
    def plot_periodset(periodset: PeriodSet, *args, axes=None, **kwargs):
        """
        Plot a :class:`PeriodSet` on the given axes as a vertical line for each timestamp.

        Params:
            periodset: The :class:`PeriodSet` to plot.
            *args: Additional arguments to pass to the plot function.
            axes: The axes to plot on. If None, the current axes are used.

        Returns:
            List with the plotted elements.

        See also:
            :func:`~pymeos.plotters.time_plotter.TimePlotter.plot_period`
        """
        periods = periodset.periods()
        line = TimePlotter.plot_period(periods[0], *args, axes=axes, **kwargs)
        kwargs.pop('label', None)
        lines = [line]
        if 'color' not in kwargs:
            kwargs['color'] = line[0].get_color()
        for p in periods[1:]:
            lines.append(TimePlotter.plot_period(p, *args, axes=axes, **kwargs))
        return lines
