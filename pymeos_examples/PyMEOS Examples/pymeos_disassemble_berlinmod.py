import datetime
import warnings

import pandas as pd
from postgis import Geometry
from pymeos import Temporal, pymeos_initialize, pymeos_finalize

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    pymeos_initialize()

    # read csv files
    trips = pd.read_csv('../data/trips.csv',
                        converters={'trip': Temporal.from_hexwkb, 'trajectory': Geometry.from_ewkb})
    print("%d trip records read.\n\n" % len(trips))

    # record the index of current instant of each trip
    # in each iteration, the current instant with minimum timestamp 
    # will be output and its index will move forward
    curr_inst_idx = [1 for i in range(len(trips))]
    num_insts = [t.num_instants for t in trips['trip']]
    MAX_DATETIME = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    # initialize the list of timestamp of current instance of each trip
    curr_inst_ts = list()
    for i in range(len(trips)):
        if curr_inst_idx[i] > 0 and curr_inst_idx[i] <= num_insts[i]:
            t = trips['trip'][i]
            curr_inst = t.instant_n(curr_inst_idx[i])
            curr_inst_ts.append(curr_inst.timestamp)
        else:
            curr_inst_ts.append(MAX_DATETIME)

    count = 0

    # output
    f = open('trip_instants.csv', 'w')
    f.write('vehicle,day,seq,geom,t\n')
    print(f"There are supposed to be {sum(num_insts)} obeservations, which might take a while...")

    while (True):
        if len([ts for ts in curr_inst_ts if ts < MAX_DATETIME]) == 0:
            break
        # write the instance to file
        selected_trip_idx = min(range(len(curr_inst_ts)), key=curr_inst_ts.__getitem__)
        row = trips.iloc[selected_trip_idx]
        selected_trip = row['trip']
        curr_inst = selected_trip.instant_n(curr_inst_idx[selected_trip_idx])
        inst_str = str(curr_inst)
        str_split = inst_str.split('@')
        f.write(f'{row.vehicle},{row.day},{row.seq},{str_split[0]},{str_split[1]}\n')
        count += 1

        # update curr instance index and timestamp
        if curr_inst_idx[selected_trip_idx] >= num_insts[selected_trip_idx]:
            # finish the trip
            curr_inst_idx[selected_trip_idx] = -1
            curr_inst_ts[selected_trip_idx] = MAX_DATETIME
        else:
            curr_inst_idx[selected_trip_idx] += 1
            next_inst = selected_trip.instant_n(curr_inst_idx[selected_trip_idx])
            curr_inst_ts[selected_trip_idx] = next_inst.timestamp

    print(f"{count} observation records written.")
    f.close()
    pymeos_finalize()
