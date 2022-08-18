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

from ..time import TimestampSet, Period, PeriodSet

print("\n# Period")

# Constructors
var = Period(string='[2019-09-08, 2019-09-10]')
print("Constructor string:", var)
var = Period(string='[2019-09-08, 2019-09-10)')
print("Constructor string:", var)
var = Period(string='(2019-09-08, 2019-09-10]')
print("Constructor string:", var)
var = Period(string='(2019-09-08, 2019-09-10)')
print("Constructor string:", var)
var = Period(lower='2019-09-08', upper='2019-09-10')
print("Constructor 2 args:", var)
var = Period(lower='2019-09-08', upper='2019-09-10', lower_inc=False, upper_inc=True)
print("Constructor 4 args:", var)

# Accessor functions
var1 = var.lower
print("lower:", var1)
var1 = var.upper
print("upper:", var1)
var1 = var.lower_inc
print("lower_inc:", var1)
var1 = var.upper_inc
print("upper_inc:", var1)
var1 = var.duration
print("duration:", var1)
var1 = var.to_periodset()
print("periodset:", var1)
var1 = var.shift(timedelta(days=3))
print("shift:", var1)

# Comparisons
var1 = Period(lower='2019-09-08', upper='2019-09-10', lower_inc=True, upper_inc=True)
var2 = Period(lower='2019-09-08', upper='2019-09-10', lower_inc=False, upper_inc=True)
print("Eq:", var1 == var2)
print("Lt:", var1 < var2)
print("Le:", var1 <= var2)
print("Gt:", var1 > var2)
print("Ge:", var1 >= var2)

print("\n# TimestampSet")

# Constructor with a single argument of type string
var = TimestampSet(string='{2019-09-08, 2019-09-10, 2019-09-11, 2019-09-12}')
print("Constructor string:   ", var)
t1 = datetime.strptime('2019-09-08', '%Y-%m-%d')
t2 = datetime.strptime('2019-09-10', '%Y-%m-%d')
t3 = datetime.strptime('2019-09-11', '%Y-%m-%d')
t4 = datetime.strptime('2019-09-12', '%Y-%m-%d')
var = TimestampSet(timestamp_list=['2019-09-08', '2019-09-10', '2019-09-11', '2019-09-12'])
print("Constructor list of strings:  ", var)
# Constructor with a single argument of type list of periods
var = TimestampSet(timestamp_list=[t1, t2, t3, t4])
print("Constructor list of datetimes:", var)

# Error
# t4 = datetime.strptime('2019-09-11', '%Y-%m-%d')
# var = TimestampSet(t1, t2, t3, t4)

# Accessor functions
var1 = var.timespan
print("timespan:", var1)
var1 = var.period
print("period:", var1)
var1 = var.num_timestamps
print("numTimestamps:", var1)
var1 = var.start_timestamp
print("startTimestamp:", var1)
var1 = var.end_timestamp
print("endTimestamp:", var1)
var1 = var.timestamp_n(1)
print("timestampN(1):", var1)
var1 = var.timestamp_n(4)
print("timestampN(4):", var1)
var1 = var.timestamps
print("timestamps:", var1)
var1 = var.shift(timedelta(days=1))
print("shift:", var1)

print("\n# PeriodSet")

# Constructor with a single argument of type string
var = PeriodSet(
    string='{[2019-09-08, 2019-09-10], [2019-09-11, 2019-09-12), [2019-09-13,2019-09-13], (2019-09-14, 2019-09-15]}')
print("Constructor string: ", var)
# Constructor with a single argument of type list of strings
var = PeriodSet(period_list=['[2019-09-08, 2019-09-10]', '[2019-09-11, 2019-09-12)',
                 '[2019-09-13,2019-09-13]', '(2019-09-14, 2019-09-15)'])
print("Constructor list of strings:", var)
# Constructor with a single argument of type list of periods
p1 = Period(string='[2019-09-08, 2019-09-10]')
p2 = Period(string='[2019-09-11, 2019-09-12)')
p3 = Period(string='[2019-09-13,2019-09-13]')
p4 = Period(string='(2019-09-14, 2019-09-15)')
var = PeriodSet(period_list=[p1, p2, p3, p4])
print("Constructor list of periods:", var)

# Error
# t4 = datetime.strptime('2019-09-11', '%Y-%m-%d')
# var = PeriodSet(p1, p2, p3, p4)

# Accessor functions
var1 = var.duration
print("duration:", var1)
var1 = var.timespan
print("timespan:", var1)
var1 = var.to_period()
print("period:", var1)
var1 = var.num_timestamps
print("numTimestamps:", var1)
var1 = var.start_timestamp
print("startTimestamp:", var1)
var1 = var.end_timestamp
print("endTimestamp:", var1)
var1 = var.timestamp_n(1)
print("timestampN(1):", var1)
var1 = var.timestamps
print("timestamps:", var1)

var1 = var.num_periods
print("numPeriods:", var1)
var1 = var.start_period
print("startPeriod:", var1)
var1 = var.end_period
print("endPeriod:", var1)
var1 = var.period_n(1)
print("periodN(1):", var1)
var1 = var.periods
print("periods:", var1)
var1 = var.shift(timedelta(days=1))
print("shift:", var1)

p1 = Period(string='[2019-09-08, 2019-09-10]')
p2 = Period(string='[2019-09-11, 2019-09-12)')
print("overlap:", p1.overlap(p2))
p2 = Period(string='[2019-09-09, 2019-09-12)')
print("overlap:", p1.overlap(p2))

p1 = Period(string='[2019-09-08, 2019-09-10]')
p2 = Period(string='[2019-09-08, 2019-09-10]')
p3 = Period(string='[2019-09-11, 2019-09-12)')
print("Period equality:", p1 == p2)
print("Period equality:", p1 == p3)

ts1 = TimestampSet(string='{2019-09-08, 2019-09-10}')
ts2 = TimestampSet(string='{2019-09-08, 2019-09-10}')
ts3 = TimestampSet(string='{2019-09-08, 2019-09-10, 2019-09-11}')
print("TimestampSet equality:", ts1 == ts2)
print("TimestampSet equality:", ts1 == ts3)

ps1 = PeriodSet(string='{[2019-09-08, 2019-09-10],[2019-09-11, 2019-09-12)}')
ps2 = PeriodSet(string='{[2019-09-08, 2019-09-10],[2019-09-11, 2019-09-12)}')
ps3 = PeriodSet(string='{[2019-09-08, 2019-09-10],[2019-09-11, 2019-09-12]}')
ps4 = PeriodSet(string='{[2019-09-11, 2019-09-12)}')
print("PeriodSet equality:", ps1 == ps2)
print("PeriodSet equality:", ps1 == ps3)
print("PeriodSet equality:", ps1 == ps4)

print("Time types equality:", p1 == ts1)
print("Time types equality:", p1 == ps1)
print("Time types equality:", ts1 == ps1)

print("representantion:", repr(p1))
print("representantion:", repr(ts1))
print("representantion:", repr(ps1))
