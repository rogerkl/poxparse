import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


"""Simple plot of pulseoximeter data

Read a file created by parse_pox_data.py and plot it with matplotlib
If a second argument is given the plot will be smoothed by this many frames (each i 4s)
"""


def main(file, mean):
    fname = os.path.basename(file)
    data = pd.read_csv(file, parse_dates=['Time'])

    fr = data['Time'].iloc[0].strftime("%m/%d/%Y %H:%M:%S")
    to = data['Time'].iloc[-1].strftime("%m/%d/%Y %H:%M:%S")
    title = "{} - {}".format(fr, to)
    non_empty = data[data['SpO2'] > 0]
    count = non_empty['SpO2'].count()
    minSpO2 = non_empty['SpO2'].min()
    maxSpO2 = non_empty['SpO2'].max()
    meanSpO2 = non_empty['SpO2'].mean()
    minHr = non_empty['Hr'].min()
    maxHr = non_empty['Hr'].max()
    meanHr = non_empty['Hr'].mean()
    # 95-100,90-94,85-89,80-84,75-79,70-74,65-69,1-64
    p95100 = 100. * non_empty['95-100'].sum()/float(count)
    p9094 = 100. * non_empty['90-94'].sum()/float(count)
    p8589 = 100. * non_empty['85-89'].sum()/float(count)
    p8084 = 100. * non_empty['80-84'].sum()/float(count)
    p7579 = 100. * non_empty['75-79'].sum()/float(count)
    p7074 = 100. * non_empty['70-74'].sum()/float(count)
    p6569 = 100. * non_empty['65-69'].sum()/float(count)
    p164 = 100. * non_empty['1-64'].sum()/float(count)
    text = "Min Spo2 = {:.0f}\n" \
           "Max Spo2 = {:.0f}\n" \
           "Mean Spo2 = {:0.2f}\n\n" \
           "Min Hr = {:.0f}\n" \
           "Max Hr = {:.0f}\n" \
           "Mean Hr = {:0.2f}\n\n" \
           "95-100 = {:0.2f}%\n" \
           "90-94 = {:0.2f}%\n" \
           "85-89 = {:0.2f}%\n" \
        "80-84 = {:0.2f}%\n" \
        "75-79 = {:0.2f}%\n" \
        "70-74 = {:0.2f}%\n" \
        "65-69 = {:0.2f}%\n" \
        "1-64 = {:0.2f}%".format(minSpO2, maxSpO2, meanSpO2, minHr, maxHr,
                                 meanHr, p95100, p9094, p8589, p8084, p7579, p7074, p6569, p164)

    # smoothing graph
    if mean != None:
        data['SpO2'] = data['SpO2'].rolling(int(mean)).mean()
        data['Hr'] = data['Hr'].rolling(int(mean)).mean()

    df = pd.DataFrame(data, columns=['Time', 'Hr', 'SpO2'])
    ax = df.plot(x='Time', style={'SpO2': 'b',
                                  'Hr': 'DarkGray'}, title=title)

    plt.figtext(0.02, 0.5, text, fontsize=10)
    plt.gcf().canvas.manager.set_window_title(fname)
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
