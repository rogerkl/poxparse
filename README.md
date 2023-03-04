# Some utilities for parsing data from NONIN 8500m Pulse Oximeter

I had an old 8500m pulse oximeter which I wrote a Windows program to extract data from back in 1997, and wanted to use it again.
Unfortunately that program was written to run on Win9x, directly accessing the serial port, so not possible to run on never Windows versions. 

Since I don't have a serial port on my PC nowadays, and I suspected that it maybe wouldn't work anyway since it uses a format with 9 databits (actually on closer inspection it is 8bit+parity, so should be able to work), I instead hooked it up to my logic analyzer and decoded the data from PulseView.

These 2 python scripts takes the data from PulseView and converts it into something that can be imported into a spreadsheet or similar.


## parse_pv_uart_ann.py
This takes data exported from PulseView and converts into a binary file with just the data bytes.

### To sample and export the data with a logic analyzer and PulseView:

Start a new session using samplerate 1MHz and 1 Gig samples (just stop when all data is received)
Lower sampling rates may work, but I found I got error's if too low.

Connect a probe from the logic analyzer to Port 2 on the NONIN and ground to Port 7 (the ones that the sensor cable is not using)
In PuilseView you can remove all channels except the one used for the probe

Add protocol debugger, UART
RX: channel should be the channel used
TX: not used
baud: rate 9600
bits: 8 
parity: odd
stop bits: 1
bit-order: lsb-first
data format: hex

Start capturing data by pressing "Arrow Up" and "On", and release them.
I think it normally sends the data in 2 bursts, first some metadata, then the actual data some seconds later.
When the second burst of data is finished it is probably finished, just wat 10-20 seconds to be sure, the stop the capture.
Then right click on the UART:RX row and choose "Export all annotations for this row"

### parsing the data from pulseview
Run 

>python parse_pv_uart_ann.py {filename}

The file should be the annotations exported from pulseview, it will then save it to a file {filename}.bin

## parse_pox_data.py

This script reads the binary data and converts in to a csv file to be read by a spreadsheet or similar.

NB I don't have the specs for the format, and could only find an early version of the source for my progrm from 97, but 
I think it is correct ... There are 3 bytes pr. data point, HR, SpO2 and the third looks like a sum of HR+SpO2, assuming thats a check the program will clear values if sum<>hr+spo2
The spec says the HR goes from 18 to 300 with reduced resolution to 2 points from 200 and up, so I guess that there should be some code to convert the values after 200 since the byte could be max 255, but I haven't done anything, since 200 is too high anyway ...

## parse the binary data
Run 

>python parse_pox_data.py {filename}

where filename is the file created earlier with binary data.
It will create one file pr. session in the data, each called {inputfile}.{number}.csv where number is the session number exported. The sessions are exported newest first.

The fields exported are 
>Time,SpO2,Hr,95-100,90-94,85-89,80-84,75-79,70-74,65-69,1-64

- **Time** Time datapoint taken (every 4 sec)
- **SpO2** SpO2 reading
- **HR** HR reading
- **95-100 etc.** To ease reporting, 1 if the SpO2 are in the range, else 0 

Since the export contains an 1/0 if the SpO2 reading is in that range or not, you could easily sum them up in the spreadsheet and calculate % based on the # of total points


### Simple plot of data

plot_pd_data.py displays a simple plot of the data from a pulse oximeter session using mathplotlib

This requires pandas and mathplotlib to be installed
Although the other scripts should work with both python 2.7 and python 3 I have only tested the plot on python 3

Run 

>python plot_pd_data.py {filename}

where input filename is a csv-file created by parse_pox_data.py script over
If you only want to show a single item on the X-Axis run with

>python plot_pd_data.py {filename} SpO2

or

>python plot_pd_data.py {filename} Hr
