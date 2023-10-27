from typing import Union

from matplotlib import pyplot as plt
from pymeos import IntSpan, FloatSpan


class SpanPlotter:
    """
    Plotter for :class:`FloatSpan` and :class:`IntSpan` objects.
    """

    @staticmethod
    def plot_span(span: Union[IntSpan, FloatSpan], *args, axes=None, **kwargs):
        """
        Plot a :class:`FloatSpan` or :class:`IntSpan` on the given axes.

        Params:
            span: The :class:`FloatSpan` or :class:`IntSpan` to plot.
            axes: The axes to plot on. If None, the current axes are used.
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.
        """
        base = axes or plt.gca()
        ll = base.axhline(
            span.lower(), *args, linestyle="-" if span.lower_inc() else "--", **kwargs
        )
        kwargs.pop("label", None)
        ul = base.axhline(
            span.upper(), *args, linestyle="-" if span.upper_inc() else "--", **kwargs
        )
        s = base.axhspan(span.lower(), span.upper(), *args, alpha=0.3, **kwargs)
        return [ll, ul, s]
