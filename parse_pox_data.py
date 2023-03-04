"""Parse data from NONIN 8500M

This script takes a binary file with data from the serial port export from NONIN 8500M
The inputfile should just be the bytes received via serial port.
The script will then look for the pulse oximeter data, parse it and output a csv file that can 
be imported in a spreadsheet or similar to produce a graph.

This is tested by using PulseView to sample the serial port, export annotations from pulseview and 
convert to a binary file by the parse_pv_uart_ann.py script, but if you get data from some other means, 
it should work as long as the raw data is exported to a binary file.



If there are more than one session in the data each session will get exported in its own file with 
a number starting at 0

The output will be written to the file(s) <inputfile>.<number>.csv 
"""

import sys
import binascii
import datetime


def ordx(s):
    if sys.version_info.major == 3:
        return s
    return ord(s)


def main(file):
    start_session = binascii.unhexlify('FEFEFC')
    end_data = binascii.unhexlify('000000000000000000000000000000000000')
    with open(file, mode="rb") as bin_file:
        contents = bin_file.read()
        sessions_start = []
        session = -1
        for i in range(len(contents)-2):
            c = contents[i:i+3]
            if c == start_session:
                sessions_start.append(i)
                session = session+1
            elif i <= (len(contents)-18) and contents[i:i+18] == end_data:
                sessions_start.append(i)
                break
        # print(sessions_start)

        for i in range(session+1):
            ofile = "{}.{}.csv".format(file, i)
            if (sessions_start[i+1]-sessions_start[i]) > 52:
                with open(ofile, "w") as outfile:
                    year = ordx(contents[sessions_start[i]+24])
                    if year > 90:
                        year = 1900+year
                    else:
                        year = 2000+year
                    month = ordx(contents[sessions_start[i]+21])
                    if month < 1:
                        month = 1
                    day = ordx(contents[sessions_start[i]+22])
                    if day < 1:
                        day = 1
                    hour = ordx(contents[sessions_start[i]+28])
                    min = ordx(contents[sessions_start[i]+25])
                    sec = ordx(contents[sessions_start[i]+27])
                    d = datetime.datetime(year, month, day, hour, min, sec)
                    print("writing {} starting at {}".format(ofile, d))
                    outfile.write(
                        "Time,SpO2,Hr,95-100,90-94,85-89,80-84,75-79,70-74,65-69,1-64\n")

                    # the data for the sessions are transferred newest datapoint first, so we go backwards

                    # seems like 6 bytes (FF FF FE FF FF FE) before the FE FE FC section that we trigger on (next session)
                    #   so index of first byte in packet is -9 bytes back from next session
                    #   50 is the last byte before the start (or end since we go backwards) of the data from the FE FE FC section we trigger on

                    for j in range(sessions_start[i+1]-9, sessions_start[i]+50, -3):
                        sum = ordx(contents[j+2])
                        spo2 = ordx(contents[j+1])
                        spo2 = spo2 if spo2 <= 100 else 0
                        hr = ordx(contents[j])
                        hr = hr if spo2 <= 100 else 0
                        if sum != (spo2+hr):
                            spo2 = 0
                            hr = 0
                        outfile.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
                            d,
                            "" if spo2 < 1 else spo2,
                            "" if spo2 < 1 else hr,
                            1 if spo2 >= 95 and spo2 <= 100 else 0,
                            1 if spo2 >= 90 and spo2 <= 94 else 0,
                            1 if spo2 >= 85 and spo2 <= 89 else 0,
                            1 if spo2 >= 80 and spo2 <= 84 else 0,
                            1 if spo2 >= 75 and spo2 <= 79 else 0,
                            1 if spo2 >= 70 and spo2 <= 74 else 0,
                            1 if spo2 >= 65 and spo2 <= 69 else 0,
                            1 if spo2 >= 1 and spo2 < 65 else 0
                        ))
                        d = d + datetime.timedelta(0, 4)


if __name__ == "__main__":
    main(sys.argv[1])
