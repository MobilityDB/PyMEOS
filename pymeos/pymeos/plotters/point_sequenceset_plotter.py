from .point_sequence_plotter import TemporalPointSequencePlotter
from ..main import TPointSeqSet


class TemporalPointSequenceSetPlotter:

    @staticmethod
    def plot_xy(sequence_set: TPointSeqSet, *args, **kwargs):
        seqs = sequence_set.sequences
        plot = TemporalPointSequencePlotter.plot_xy(seqs[0], *args, **kwargs)
        color = plot[0].get_color()
        for seq in seqs[1:]:
            plot = TemporalPointSequencePlotter.plot_xy(seq, color=color, *args, **kwargs)
        return plot
