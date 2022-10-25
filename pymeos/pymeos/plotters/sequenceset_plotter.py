from .sequence_plotter import TemporalSequencePlotter
from ..temporal import TSequenceSet


class TemporalSequenceSetPlotter:

    @classmethod
    def plot(cls, sequence_set: TSequenceSet, *args, **kwargs):
        seqs = sequence_set.sequences
        plot = TemporalSequencePlotter.plot(seqs[0], *args, **kwargs)
        color = plot[0].get_color()
        for seq in seqs[1:]:
            plot = TemporalSequencePlotter.plot(seq, color=color, *args, **kwargs)
        return plot
