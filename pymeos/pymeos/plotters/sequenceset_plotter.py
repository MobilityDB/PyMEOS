from typing import List, Union

from .sequence_plotter import TemporalSequencePlotter
from .. import TSequence
from ..temporal import TSequenceSet


class TemporalSequenceSetPlotter:

    @staticmethod
    def plot(sequence_set: Union[TSequenceSet, List[TSequence]], *args, **kwargs):
        seqs = sequence_set.sequences if isinstance(sequence_set, TSequenceSet) else sequence_set
        plot = TemporalSequencePlotter.plot(seqs[0], *args, **kwargs)
        if 'color' not in kwargs:
            kwargs['color'] = plot[0].get_color()
        kwargs.pop('label', None)
        for seq in seqs[1:]:
            plot = TemporalSequencePlotter.plot(seq, *args, **kwargs)
        return plot
