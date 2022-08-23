###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################

from datetime import datetime, timedelta

from dateutil.parser import parse

from ..main import TBoolInst, TBoolInstSet, TBoolSeq, TBoolSeqSet
from ..time import TimestampSet, Period, PeriodSet

print("\nConstructors for TBoolInst")
inst = TBoolInst(string='True@2019-09-08')
print(inst)
inst = TBoolInst(value='True', timestamp='2019-09-08')
print(inst)
t = parse('2019-09-08')
inst = TBoolInst(value='True', timestamp=t)
print(inst)

print("\nConstructors for TBoolInstSet")
ti = TBoolInstSet(string='{True@2019-09-08, False@2019-09-09, False@2019-09-10}')
print(ti)
ti = TBoolInstSet(instant_list=['True@2019-09-08', 'False@2019-09-09', 'False@2019-09-10'])
print(ti)
t1 = TBoolInst(value=True, timestamp='2019-09-08')
t2 = TBoolInst(value=False, timestamp='2019-09-09')
t3 = TBoolInst(value=False, timestamp='2019-09-10')
ti = TBoolInstSet(instant_list=[t1, t2, t3])
print(ti)

print("\nConstructors for TBoolSeq")
seq = TBoolSeq(string='[True@2019-09-08, False@2019-09-09, False@2019-09-10]')
print(seq)
seq = TBoolSeq(instant_list=['True@2019-09-08', 'False@2019-09-09', 'False@2019-09-10'])
print(seq)
t4 = TBoolInst(value=True, timestamp='2019-09-08')
t5 = TBoolInst(value=False, timestamp='2019-09-09')
t6 = TBoolInst(value=False, timestamp='2019-09-10')
seq = TBoolSeq(instant_list=[t4, t5, t6])
print(seq)
seq = TBoolSeq(instant_list=[t1, t2, t3], lower_inc=False, upper_inc=True)
print(seq)

print("\nConstructors for TBoolSeqSet")
ts = TBoolSeqSet(string='{[True@2019-09-08, False@2019-09-09, False@2019-09-10],[False@2019-09-11, True@2019-09-12]}')
print('Hey')
print(ts)
ts = TBoolSeqSet(sequence_list=['[True@2019-09-08, False@2019-09-09, False@2019-09-10]', '[False@2019-09-11, True@2019-09-12]'])
print(ts)
seq1 = TBoolSeq(string='[True@2019-09-08, False@2019-09-09, False@2019-09-10]')
seq2 = TBoolSeq(string='[False@2019-09-11, True@2019-09-12]')
ts = TBoolSeqSet(sequence_list=[seq1, seq2])
print(ts)

print("\n__class__ ")
print(inst.__class__.__name__)
print(ti.__class__.__name__)
print(seq.__class__.__name__)
print(ts.__class__.__name__)

print("\n__bases__ ")
print(inst.__class__.__bases__)
print(ti.__class__.__bases__)
print(seq.__class__.__bases__)
print(ts.__class__.__bases__)

print("\ntempSubtype")
print(inst.temp_subtype())
print(ti.temp_subtype())
print(seq.temp_subtype())
print(ts.temp_subtype())

print("\ninterpolation")
print(seq.interpolation)
print(ts.interpolation)

print("\ngetValue")
print(inst.value)

print("\ngetValues")
print(inst.values)
print(ti.values)
print(seq.values)
print(ts.values)

print("\nstart_value")
print(inst.start_value)
print(ti.start_value)
print(seq.start_value)
print(ts.start_value)

print("\nend_value")
print(inst.end_value)
print(ti.end_value)
print(seq.end_value)
print(ts.end_value)

print("\nmin_value")
print(inst.min_value)
print(ti.min_value)
print(seq.min_value)
print(ts.min_value)

print("\nmax_value")
print(inst.max_value)
print(ti.max_value)
print(seq.max_value)
print(ts.max_value)

print("\ngetTimestamp")
print(inst.timestamp)

print("\ngetTime")
print(inst.time)
print(ti.time)
print(seq.time)
print(ts.time)

print("\nduration")
print(inst.duration)
print(ti.duration)
print(seq.duration)
print(ts.duration)

print("\ntimespan")
print(inst.timespan)
print(ti.timespan)
print(seq.timespan)
print(ts.timespan)

print("\nperiod")
print(inst.period)
print(ti.period)
print(seq.period)
print(ts.period)

print("\nnum_instants")
print(inst.num_instants)
print(ti.num_instants)
print(seq.num_instants)
print(ts.num_instants)

print("\nstart_instant")
print(inst.start_instant)
print(ti.start_instant)
print(seq.start_instant)
print(ts.start_instant)

print("\nend_instant")
print(inst.end_instant)
print(ti.end_instant)
print(seq.end_instant)
print(ts.end_instant)

print("\ninstant_n")
print(inst.instant_n(1))
print(ti.instant_n(1))
print(seq.instant_n(1))
print(ts.instant_n(1))

print("\ninstants")
print(inst.instants)
print(ti.instants)
print(seq.instants)
print(ts.instants)

print("\nnum_timestamps")
print(inst.num_timestamps)
print(ti.num_timestamps)
print(seq.num_timestamps)
print(ts.num_timestamps)

print("\nstart_timestamp")
print(inst.start_timestamp)
print(ti.start_timestamp)
print(seq.start_timestamp)
print(ts.start_timestamp)

print("\nend_timestamp")
print(inst.end_timestamp)
print(ti.end_timestamp)
print(seq.end_timestamp)
print(ts.end_timestamp)

print("\ntimestamp_n")
print(inst.timestamp_n(1))
print(ti.timestamp_n(1))
print(seq.timestamp_n(1))
print(ts.timestamp_n(1))

print("\ntimestamps")
print(inst.timestamps)
print(ti.timestamps)
print(seq.timestamps)
print(ts.timestamps)

print("\nnumSequences")
print(seq.num_sequences)
print(ts.num_sequences)

print("\nstartSequence")
print(seq.start_sequence)
print(ts.start_sequence)

print("\nendSequence")
print(seq.end_sequence)
print(ts.end_sequence)

print("\nsequenceN")
print(seq.sequence_n(1))
print(ts.sequence_n(1))

print("\nsequences")
print(seq.sequences)
print(ts.sequences)

print("\nshift")
print(inst.shift(timedelta(days=1)))
print(ti.shift(timedelta(days=1)))
print(seq.shift(timedelta(days=1)))
print(ts.shift(timedelta(days=1)))

print("\nintersectsTimestamp")
t = datetime.strptime('2019-09-09', '%Y-%m-%d')
print(inst.intersects(t))
print(ti.intersects(t))
print(seq.intersects(t))
print(ts.intersects(t))

print("\nintersectsTimestampSet")
tss = TimestampSet(string='{2019-09-09, 2019-09-10}')
print(inst.intersects(tss))
print(ti.intersects(tss))
print(seq.intersects(tss))
print(ts.intersects(tss))

print("\nintersectsPeriod")
p = Period(lower='2019-09-09', upper='2019-09-10', lower_inc=True, upper_inc=True)
print(inst.intersects(p))
print(ti.intersects(p))
print(seq.intersects(p))
print(ts.intersects(p))

print("\nintersectsPeriodSet")
ps = PeriodSet(string='{[2019-09-09,2019-09-10], [2019-09-11,2019-09-12]}')
print(inst.intersects(ps))
print(ti.intersects(ps))
print(seq.intersects(ps))
print(ts.intersects(ps))


print("\nNOT")
print(-inst)