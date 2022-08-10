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
from mobilitydb.time import TimestampSet, Period, PeriodSet
from mobilitydb.main import TFloat, TFloatInst, TFloatInstSet, TFloatSeq, TFloatSeqSet


print("\nConstructors for TFloatInst")
inst = TFloatInst('10@2019-09-08')
print(inst)
inst = TFloatInst('10', '2019-09-08')
print(inst)
t = parse('2019-09-08')
inst = TFloatInst(10.0, t)
print(inst)

print("\nConstructors for TFloatInstSet")
ti = TFloatInstSet('{10@2019-09-08, 20@2019-09-09, 20@2019-09-10}')
print(tinstset)
ti = TFloatInstSet('10@2019-09-08', '20@2019-09-09', '20@2019-09-10')
print(tinstset)
ti = TFloatInstSet(['10@2019-09-08', '20@2019-09-09', '20@2019-09-10'])
print(tinstset)
t1 = TFloatInst('10@2019-09-08')
t2 = TFloatInst('20@2019-09-09')
t3 = TFloatInst('20@2019-09-10')
ti = TFloatInstSet(t1, t2, t3)
print(tinstset)
ti = TFloatInstSet([t1, t2, t3])
print(tinstset)

print("\nConstructors for TFloatSeq")
seq = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
print(seq)
seq = TFloatSeq(['10@2019-09-08', '20@2019-09-09', '20@2019-09-10'])
print(seq)
seq = TFloatSeq([t1, t2, t3])
print(seq)
seq = TFloatSeq([t1, t2, t3], False, True)
print(seq)

print("\nConstructors for TFloatSeqSet")
ts = TFloatSeqSet('{[10@2019-09-08, 20@2019-09-09, 20@2019-09-10],[15@2019-09-11, 30@2019-09-12]}')
print(ts)
ts = TFloatSeqSet(['[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]', '[15@2019-09-11, 30@2019-09-12]'])
print(ts)
seq1 = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
seq2 = TFloatSeq('[15@2019-09-11, 30@2019-09-12]')
ts = TFloatSeqSet([seq1, seq2])
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

print("\nRepresentation")
print(repr(inst))
print(repr(tinstset))
print(repr(seq))
print(repr(ts))

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

print("\nstartValue")
print(inst.start_value)
print(ti.start_value)
print(seq.start_value)
print(ts.start_value)

print("\nendValue")
print(inst.end_value)
print(ti.end_value)
print(seq.end_value)
print(ts.end_value)

print("\nminValue")
print(inst.min_value)
print(ti.min_value)
print(seq.min_value)
print(ts.min_value)

print("\nmaxValue")
print(inst.max_value)
print(ti.max_value)
print(seq.max_value)
print(ts.max_value)

print("\nvalueRange")
print(inst.valueRange)
print(ti.valueRange)
print(seq.valueRange)
print(ts.valueRange)

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

print("\nnumInstants")
print(inst.num_instants)
print(ti.num_instants)
print(seq.num_instants)
print(ts.num_instants)

print("\nstartInstant")
print(inst.start_instant)
print(ti.start_instant)
print(seq.start_instant)
print(ts.start_instant)

print("\nendInstant")
print(inst.end_instant)
print(ti.end_instant)
print(seq.end_instant)
print(ts.end_instant)

print("\ninstantN")
print(inst.instant_n(1))
print(ti.instant_n(1))
print(seq.instant_n(1))
print(ts.instant_n(1))

print("\ninstants")
print(inst.instants)
print(ti.instants)
print(seq.instants)
print(ts.instants)

print("\nnumTimestamps")
print(inst.num_timestamps)
print(ti.num_timestamps)
print(seq.num_timestamps)
print(ts.num_timestamps)

print("\nstartTimestamp")
print(inst.start_timestamp)
print(ti.start_timestamp)
print(seq.start_timestamp)
print(ts.start_timestamp)

print("\nendTimestamp")
print(inst.end_timestamp)
print(ti.end_timestamp)
print(seq.end_timestamp)
print(ts.end_timestamp)

print("\ntimestampN")
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
print(inst.intersects_timestamp(t))
print(ti.intersects_timestamp(t))
print(seq.intersects_timestamp(t))
print(ts.intersects_timestamp(t))

print("\nintersectsTimestampSet")
tss = TimestampSet('{2019-09-09, 2019-09-10}')
print(inst.intersects_timestamp_set(tss))
print(ti.intersects_timestamp_set(tss))
print(seq.intersects_timestamp_set(tss))
print(ts.intersects_timestamp_set(tss))

print("\nintersectsPeriod")
p = Period('2019-09-09', '2019-09-10', True, True)
print(inst.intersects_period(p))
print(ti.intersects_period(p))
print(seq.intersects_period(p))
print(ts.intersects_period(p))

print("\nintersectsPeriodSet")
ps = PeriodSet('{[2019-09-09,2019-09-10], [2019-09-11,2019-09-12]}')
print(inst.intersects_period_set(ps))
print(ti.intersects_period_set(ps))
print(seq.intersects_period_set(ps))
print(ts.intersects_period_set(ps))

print("\nequality for TInstant")
inst1 = TFloatInst('1@2019-09-09')
inst2 = TFloatInst('1.0@2019-09-09 00:00:00')
inst3 = TFloatInst('1.1@2019-09-09')
inst4 = TFloatInst('1@2019-09-10')
print(inst1 == inst2)
print(inst1 == inst3)
print(inst1 == inst4)

print("\nequality for TInstantSet")
ti1 = TFloatInstSet('{10@2019-09-08, 20@2019-09-09, 20@2019-09-10}')
ti2 = TFloatInstSet('{10@2019-09-08, 20@2019-09-09, 20@2019-09-10}')
ti3 = TFloatInstSet('{10@2019-09-08, 20@2019-09-10}')
print(ti1 == ti2)
print(ti1 == ti3)

print("\nequality for TSequence")
seq1 = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
seq2 = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
seq3 = TFloatSeq('[10.1@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
seq4 = TFloatSeq('(10@2019-09-08, 20@2019-09-09, 20@2019-09-10]')
seq5 = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10)')
seq6 = TFloatSeq('[10@2019-09-08, 20@2019-09-09, 20@2019-09-10]', interp='Stepwise')
print(seq1 == seq2)
print(seq1 == seq3)
print(seq1 == seq4)
print(seq1 == seq5)
print(seq1 == seq6)

print("\nequality for TSequenceSet")
ts1 = TFloatSeqSet('{[10@2019-09-08, 20@2019-09-09, 20@2019-09-10],[10@2019-09-11, 20@2019-09-12]}')
ts2 = TFloatSeqSet('{[10@2019-09-08, 20@2019-09-09, 20@2019-09-10],[10@2019-09-11, 20@2019-09-12]}')
ts3 = TFloatSeqSet('{[10@2019-09-08, 20@2019-09-09, 20@2019-09-10],[10@2019-09-11]}')
ts4 = TFloatSeqSet('{[10@2019-09-08, 20@2019-09-09, 20@2019-09-10],[10@2019-09-11, 20@2019-09-12]}', interp='Stepwise')
print(ts1 == ts2)
print(ts1 == ts3)
print(ts1 == ts4)

print("*** Manual ***")
p = TFloatInstSet('{10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01}')
print(p)
p = TFloatInstSet('10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01')
print(p)
p = TFloatInstSet(TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01'))
print(p)
p = TFloatInstSet(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
print(p)
p = TFloatInstSet([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])
print(p)

print("*** Manual ***")
p = TFloatSeq('[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')
print(p)
p = TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')
print(p)
p = TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
print(p)
p = TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])
print(p)
p = TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'], True, True, 'Stepwise')
print(p)
p = TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')], True, True, 'Stepwise')
print(p)

print("*** Manual ***")
p = TFloatSeqSet('{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')
print(p)
p = TFloatSeqSet('Interp=Stepwise;{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')
print(p)
p = TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'])
print(p)
p = TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Linear')
print(p)
p = TFloatSeqSet(['Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]', 'Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Stepwise')
print(p)
p = TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')])
print(p)
p = TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'),  TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Linear')
print(p)
p = TFloatSeqSet([TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Stepwise')
print(p)
