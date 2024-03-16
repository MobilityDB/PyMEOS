from matplotlib import pyplot as plt

from .range_plotter import SpanPlotter
from .time_plotter import TimePlotter
from ..boxes import TBox, STBox


class BoxPlotter:
    """ """

    @staticmethod
    def plot_tbox(tbox: TBox, *args, axes=None, **kwargs):
        """
        Plot a TBox on the given axes. If the TBox has only a temporal or spatial dimension, this is equivalent
        to plotting the corresponding TsTzSpan or Span respectively.

        Params:
            tbox: The :class:`TBox` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.

        See Also:
            :func:`~pymeos.plotters.range_plotter.RangePlotter.plot_range`,
            :func:`~pymeos.plotters.time_plotter.TimePlotter.plot_tstzspan`
        """
        if not tbox.has_t:
            return SpanPlotter.plot_span(
                tbox.to_floatspan(), *args, axes=axes, **kwargs
            )
        if not tbox.has_x:
            return TimePlotter.plot_tstzspan(
                tbox.to_tstzspan(), *args, axes=axes, **kwargs
            )
        return BoxPlotter._plot_box(
            tbox.tmin(),
            tbox.tmax(),
            tbox.xmin(),
            tbox.xmax(),
            *args,
            axes=axes,
            **kwargs,
        )

    @staticmethod
    def plot_stbox_xy(stbox: STBox, *args, axes=None, **kwargs):
        """
        Plot an STBox on the given axes. Plots the x and y dimensions.

        Params:
            stbox: The :class:`STBox` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        return BoxPlotter._plot_box(
            stbox.xmin(),
            stbox.xmax(),
            stbox.ymin(),
            stbox.ymax(),
            *args,
            axes=axes,
            **kwargs,
        )

    @staticmethod
    def plot_stbox_xt(stbox: STBox, *args, axes=None, **kwargs):
        """
        Plot an STBox on the given axes. Plots the x and t dimensions.

        Params:
            stbox: The :class:`STBox` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        return BoxPlotter._plot_box(
            stbox.tmin(),
            stbox.tmax(),
            stbox.xmin(),
            stbox.xmax(),
            *args,
            axes=axes,
            **kwargs,
        )

    @staticmethod
    def plot_stbox_yt(stbox: STBox, *args, axes=None, **kwargs):
        """
        Plot an STBox on the given axes. Plots the y and t dimensions.

        Params:
            stbox: The :class:`STBox` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        return BoxPlotter._plot_box(
            stbox.tmin(),
            stbox.tmax(),
            stbox.ymin(),
            stbox.ymax(),
            *args,
            axes=axes,
            **kwargs,
        )

    @staticmethod
    def _plot_box(
        xmin,
        xmax,
        ymin,
        ymax,
        *args,
        axes=None,
        rotate_xticks=True,
        draw_filling=True,
        **kwargs,
    ):
        """
        Plot a box on the given axes.

        Params:
            xmin: The minimum x value.
            xmax: The maximum x value.
            ymin: The minimum y value.
            ymax: The maximum y value.
            axes: The axes to plot on. If None, the current axes are used.
            rotate_xticks: Whether to rotate the xticks by 45 degrees.
            draw_filling: Whether to draw a filling.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        plot = base.plot(
            [xmin, xmax, xmax, xmin, xmin],
            [ymin, ymin, ymax, ymax, ymin],
            *args,
            **kwargs,
        )

        if "color" not in kwargs:
            kwargs["color"] = plot[0].get_color()
        kwargs.pop("label", None)

        return_array = [plot]

        if draw_filling:
            f = base.fill_between(
                [xmin, xmax], [ymax, ymax], [ymin, ymin], *args, alpha=0.3, **kwargs
            )
            return_array.append(f)

        if rotate_xticks:
            base.tick_params(axis="x", rotation=45)

        return return_array
