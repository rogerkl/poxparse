import sys
import pandas as pd
import matplotlib.pyplot as plt

"""Simple plot of pulseoximeter data 

Read a file created by parse_pox_data.py and plot it with matplotlib
If SpO2 or Hr is given as second parameter it will only show that data, else default is showing both
"""


def main(file, axis):
    data = pd.read_csv(file, parse_dates=['Time'])
    if axis != None:
        df = pd.DataFrame(data, columns=['Time', axis])
        ax = df.plot(x='Time')
    else:
        df = pd.DataFrame(data, columns=['Time', 'Hr', 'SpO2'])
        ax = df.plot(x='Time', style={'SpO2': 'b', 'Hr': 'DarkGray'})

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
