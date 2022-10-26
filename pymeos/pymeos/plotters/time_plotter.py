from datetime import datetime

from matplotlib import pyplot as plt

from ..time import TimestampSet, Period, PeriodSet


class TimePlotter:

    @staticmethod
    def plot_timestamp(timestamp: datetime, *args, axes=None, **kwargs):
        base = axes or plt.gca()
        return base.axvline(timestamp, *args, **kwargs)

    @staticmethod
    def plot_timestampset(timestampset: TimestampSet, *args, axes=None, **kwargs):
        base = axes or plt.gca()
        stamps = timestampset.timestamps
        plot = base.axvline(stamps[0], *args, **kwargs)
        plots = [plot]
        for stamp in stamps[1:]:
            plots.append(base.axvline(stamp, *args, color=plot.get_color(), **kwargs))
        return plots

    @staticmethod
    def plot_period(period: Period, *args, axes=None, **kwargs):
        base = axes or plt.gca()
        ll = base.axvline(period.lower, *args, linestyle='-' if period.lower_inc else '--', **kwargs)
        ul = base.axvline(period.upper, *args, linestyle='-' if period.upper_inc else '--', **kwargs)
        s = base.axvspan(period.lower, period.upper, *args, alpha=0.3, **kwargs)
        return [ll, ul, s]

    @staticmethod
    def plot_periodset(periodset: PeriodSet, *args, axes=None, **kwargs):
        periods = periodset.periods
        line = TimePlotter.plot_period(periods[0], *args, axes=axes, **kwargs)
        lines = [line]
        for p in periods[1:]:
            lines.append(TimePlotter.plot_period(p, *args, axes=axes, color=line[0].get_color(), **kwargs))
        return lines
