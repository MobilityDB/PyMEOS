from typing import Union, List

from .point_sequence_plotter import TemporalPointSequencePlotter
from .. import TPointSeq
from ..main import TPointSeqSet


class TemporalPointSequenceSetPlotter:

    @staticmethod
    def plot_xy(sequence_set: Union[TPointSeqSet, List[TPointSeq]], *args, **kwargs):
        seqs = sequence_set.sequences() if isinstance(sequence_set, TPointSeqSet) else sequence_set
        plot = TemporalPointSequencePlotter.plot_xy(seqs[0], *args, **kwargs)
        if 'color' not in kwargs:
            kwargs['color'] = plot[0].get_color()
        kwargs.pop('label', None)
        for seq in seqs[1:]:
            plot = TemporalPointSequencePlotter.plot_xy(seq, *args,  **kwargs)
        return plot
