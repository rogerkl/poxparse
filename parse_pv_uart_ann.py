"""PulseView UART annotation parser

This script takes a file created by PulseView UART protocol decoder.
In PulseView, right click somwwhere in the UART:RX row and choose "Export all annotations for this row"
or if you want to export from somwehere in the timeline, choose "Export all annotations for this row, starting here"

This will lokk for lines with 
UART: RX: Start bit
UART: RX: <Data>
UART: RX: Parity bit
UART: RX: Stop bit

And if it matches write the data as binary to the file <inputfile>.bin
"""

import sys
import binascii


def stripRx(line):
    if "UART: RX: " in line:
        return line[(line.index("UART: RX: ")+10):].strip()
    return None


def main(file):
    with open(file) as infile:
        ofile = file+".bin"
        print("parsing "+file+" into binary file "+ofile)
        with open(ofile, "wb") as outfile:
            line = infile.readline()
            while line:
                if "UART: RX: " in line:
                    code = stripRx(line)
                    if code == "Start bit":
                        line = infile.readline()
                        hex = stripRx(line)
                        line = infile.readline()
                        code = stripRx(line)
                        if code == "Parity bit":
                            line = infile.readline()
                            code = stripRx(line)
                            if code == "Stop bit":
                                outfile.write(binascii.unhexlify(hex))
                line = infile.readline()


if __name__ == "__main__":
    main(sys.argv[1])
