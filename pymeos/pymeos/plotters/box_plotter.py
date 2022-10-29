from matplotlib import pyplot as plt

from .range_plotter import RangePlotter
from .time_plotter import TimePlotter
from ..boxes import TBox, STBox


class BoxPlotter:

    @staticmethod
    def plot_tbox(tbox: TBox, *args, axes=None, **kwargs):
        if not tbox.has_t:
            return RangePlotter.plot_range(tbox.to_floatrange(), *args, axes=axes, **kwargs)
        if not tbox.has_x:
            return TimePlotter.plot_period(tbox.to_period(), *args, axes=axes, **kwargs)
        return BoxPlotter._plot_box(tbox.tmin, tbox.tmax, tbox.xmin, tbox.xmax, *args, axes=axes, **kwargs)

    @staticmethod
    def plot_stbox_xy(stbox: STBox, *args, axes=None, **kwargs):
        return BoxPlotter._plot_box(stbox.xmin, stbox.xmax, stbox.ymin, stbox.ymax, *args, axes=axes, **kwargs)

    @staticmethod
    def _plot_box(xmin, xmax, ymin, ymax, *args, axes=None, **kwargs):
        base = axes or plt.gca()
        plot = base.plot([xmin, xmax, xmax, xmin, xmin],
                         [ymin, ymin, ymax, ymax, ymin],
                         *args, **kwargs)
        f = base.fill_between([xmin, xmax], [ymax, ymax], [ymin, ymin], *args,
                              color=plot[0].get_color(), alpha=0.3, **kwargs)

        base.tick_params(axis="x", rotation=45)
        return [plot, f]
