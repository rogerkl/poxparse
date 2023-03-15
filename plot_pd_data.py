import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


"""Simple plot of pulseoximeter data

Read a file created by parse_pox_data.py and plot it with matplotlib
If a second argument is given the plot will be smoothed by this many frames (each i 4s)
"""


def countEpisodes(df, meanSpO2, trigger_below):
    below = trigger_below*meanSpO2
    aspo2 = []
    result = []
    lowest = 100
    start = 0
    for index, row in df.iterrows():
        aspo2.append(row['SpO2'])
        fspo2 = float(row['SpO2'])
        if index > 0:
            if fspo2 < below:
                if start == 0:
                    start = index
                if row['SpO2'] <= lowest:
                    for i in range(start, index):
                        result[i] = 0
                    result.append(1)
                    lowest = row['SpO2']
                else:
                    result.append(0)
            else:
                result.append(0)
                lowest = 100
                start = 0
        else:
            result.append(0)
    return result


def main(file, mean, trigger_percent):
    trigger_below = float(100-trigger_percent)/100.
    fname = os.path.basename(file)
    data = pd.read_csv(file, parse_dates=['Time'])

    fr = data['Time'].iloc[0].strftime("%d/%m/%Y %H:%M:%S")
    to = data['Time'].iloc[-1].strftime("%d/%m/%Y %H:%M:%S")

    dur_hours = float(
        (data['Time'].iloc[-1]-data['Time'].iloc[0]).total_seconds())/3600.

    title = "{} - {}".format(fr, to)
    non_empty = data[data['SpO2'] > 0]
    count = non_empty['SpO2'].count()
    minSpO2 = non_empty['SpO2'].min()
    maxSpO2 = non_empty['SpO2'].max()
    meanSpO2 = non_empty['SpO2'].mean()
    minHr = non_empty['Hr'].min()
    maxHr = non_empty['Hr'].max()
    meanHr = non_empty['Hr'].mean()

    # baseline ... remove datapoint below trigger_percent of mean
    # repeat to get a stable number
    below = round(trigger_below*meanSpO2)
    not_below = data[data['SpO2'] > below]
    for i in range(10):
        below = round(trigger_below*not_below['SpO2'].mean())
        not_below = data[data['SpO2'] > below]
    baseline = not_below['SpO2'].mean()

    data['episodes'] = countEpisodes(data, baseline, trigger_below)
    # 95-100,90-94,85-89,80-84,75-79,70-74,65-69,1-64
    p95100 = 100. * non_empty['95-100'].sum()/float(count)
    p9094 = 100. * non_empty['90-94'].sum()/float(count)
    p8589 = 100. * non_empty['85-89'].sum()/float(count)
    p8084 = 100. * non_empty['80-84'].sum()/float(count)
    p7579 = 100. * non_empty['75-79'].sum()/float(count)
    p7074 = 100. * non_empty['70-74'].sum()/float(count)
    p6569 = 100. * non_empty['65-69'].sum()/float(count)
    p164 = 100. * non_empty['1-64'].sum()/float(count)
    sumdips = data['episodes'].sum()
    dipsprhour = float(sumdips)/dur_hours

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
        "1-64 = {:0.2f}%\n\n" \
        "SpO2 baseline = {:0.2f}%\n\n" \
        "#episodes {:.0f}%\n below baseline = {:.0f}\n\n" \
        "#episodes/hour = {:0.2f}".format(minSpO2, maxSpO2, meanSpO2, minHr, maxHr,
                                          meanHr, p95100, p9094, p8589, p8084, p7579, p7074, p6569, p164,
                                          baseline, trigger_percent, sumdips, dipsprhour)

    # smoothing graph
    if mean != None and mean > 0:
        data['SpO2'] = data['SpO2'].rolling(mean).mean()
        data['Hr'] = data['Hr'].rolling(mean).mean()

    data['episodes'] = data['episodes'] * data['SpO2']

    df = pd.DataFrame(data, columns=['Time', 'Hr', 'episodes', 'SpO2'])
    ax = df.plot(x='Time', style={'SpO2': 'b',
                                  'Hr': 'Green', 'episodes': 'Red'}, title=title)
    ax.lines[0].set_alpha(0.5)
    ax.lines[1].set_alpha(0.5)
    ax.set_ylim(50, 110)

    plt.figtext(0.02, 0.5, text, fontsize=10)
    plt.gcf().canvas.manager.set_window_title(fname)
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1],
         int(sys.argv[2]) if len(sys.argv) > 2 else None,
         int(sys.argv[3]) if len(sys.argv) > 3 else 3)
