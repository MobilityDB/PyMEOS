from matplotlib import pyplot as plt
from spans import floatrange


class RangePlotter:

    @staticmethod
    def plot_range(range: floatrange, *args, axes=None, **kwargs):
        base = axes or plt.gca()
        ll = base.axhline(range.lower, *args, linestyle='-' if range.lower_inc else '--', **kwargs)
        ul = base.axhline(range.upper, *args, linestyle='-' if range.upper_inc else '--', **kwargs)
        s = base.axhspan(range.lower, range.upper, *args, alpha=0.3, **kwargs)
        return [ll, ul, s]
