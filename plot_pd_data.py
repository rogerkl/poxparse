import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque
from statistics import mean

TIME = 'Time'
SPO2 = 'SpO2'
HR = 'Hr'

"""Simple plot of pulseoximeter data

Read a file created by parse_pox_data.py and plot it with matplotlib
If a second argument is given the plot will be smoothed by this many frames (each i 4s)
"""


def countEpisodesRollingMean(df, meanFrames, percent):
    d = deque([], meanFrames)
    meansp02 = 0
    result = []
    prev = 0
    prevprev = 0
    for index, row in df.iterrows():
        if len(d) > 0:
            meansp02 = mean(d)

        fspo2 = float(row[SPO2])
        # since each frame 4s use mean between i-1 and i-2 to get 10 seconds (2.5 frames)
        # trigger if below percent % of rolling mean, and downward trend for at least 10s.
        if fspo2 < meansp02*(1 - percent/100.) and (fspo2 < prev and prev < ((prev + prevprev)/2.)):
            result.append(1)
            # if passed the threshold we keep the mean as it was before
            d.append(meansp02)
        else:
            result.append(0)
            # rolling means since maxSize for deque
            d.append(fspo2)
            prevprev = prev
            prev = fspo2

    # count only onset of drop - so remove if already in an episode
    result2 = []
    for idx, x in enumerate(result):
        if x == 1 and idx > 0 and result[idx-1] == 0:
            result2.append(1)
        else:
            result2.append(0)

    return result2


def main(file, mean, saveFormat):
    fname = os.path.basename(file)
    data = pd.read_csv(file, parse_dates=[TIME])

    fr = data[TIME].iloc[0].strftime("%d/%m/%Y %H:%M:%S")
    to = data[TIME].iloc[-1].strftime("%d/%m/%Y %H:%M:%S")

    dur_hours = float(
        (data[TIME].iloc[-1]-data[TIME].iloc[0]).total_seconds())/3600.

    title = "{} - {}".format(fr, to)
    non_empty = data[data[SPO2] > 0]
    count = non_empty[SPO2].count()
    minSpO2 = non_empty[SPO2].min()
    maxSpO2 = non_empty[SPO2].max()
    meanSpO2 = non_empty[SPO2].mean()
    minHr = non_empty[HR].min()
    maxHr = non_empty[HR].max()
    meanHr = non_empty[HR].mean()

    # Sleep-related breathing disorders in adults: recommendations for syndrome definition and measurement techniques in clinical research. The Report of an American Academy of Sleep Medicine Task Force. Sleep. 1999; 22:667-89
    # Baseline is defined as the mean amplitude of stable breathing and oxygenation in the two minutes preceding onset of the event

    data['episodes4'] = countEpisodesRollingMean(data, 30, 4.)
    data['episodes3'] = countEpisodesRollingMean(data, 30, 3.)

    # 95-100,90-94,85-89,80-84,75-79,70-74,65-69,1-64
    p95100 = 100. * non_empty['95-100'].sum()/float(count)
    p9094 = 100. * non_empty['90-94'].sum()/float(count)
    p8589 = 100. * non_empty['85-89'].sum()/float(count)
    p8084 = 100. * non_empty['80-84'].sum()/float(count)
    p7579 = 100. * non_empty['75-79'].sum()/float(count)
    p7074 = 100. * non_empty['70-74'].sum()/float(count)
    p6569 = 100. * non_empty['65-69'].sum()/float(count)
    p164 = 100. * non_empty['1-64'].sum()/float(count)
    sumdips4 = data['episodes4'].sum()
    sumdips3 = data['episodes3'].sum()
    dipsprhour4 = float(sumdips4)/dur_hours
    dipsprhour3 = float(sumdips3)/dur_hours

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
        "#drops below 4% = {:.0f}\n" \
        "#drops/hour {:0.2f}\n\n" \
        "#drops below 3% = {:.0f}\n" \
        "#drops/hour = {:0.2f}".format(minSpO2, maxSpO2, meanSpO2, minHr, maxHr,
                                       meanHr, p95100, p9094, p8589, p8084, p7579, p7074, p6569, p164,
                                       sumdips4, dipsprhour4, sumdips3, dipsprhour3)

    data['drops below 4%'] = data['episodes4'] * data[SPO2]

    # smoothing graph
    if mean != None and mean > 0:
        data[SPO2] = data[SPO2].rolling(mean).mean()
        data[HR] = data[HR].rolling(mean).mean()

    df = pd.DataFrame(data, columns=[TIME, HR, 'drops below 4%', SPO2])

    plt.rcParams['figure.figsize'] = [11.7, 8.3]
    plt.rcParams.update({'font.size': 6})

    ax = df.plot(x=TIME, style={SPO2: 'b',
                                HR: 'Green', 'drops below 4%': 'Red'}, title=title)
    ax.lines[0].set_alpha(0.5)
    ax.lines[1].set_alpha(0.35)
    ax.set_ylim(50, 110)

    plt.figtext(0.02, 0.5, text, fontsize=6)
    plt.gcf().canvas.manager.set_window_title(fname)
    if saveFormat != None:
        plt.savefig(file+"."+saveFormat,
                    # bbox_inches='tight',
                    orientation='landscape', format=saveFormat)
    else:
        plt.show()


if __name__ == "__main__":
    main(sys.argv[1],
         int(sys.argv[2]) if len(sys.argv) > 2 else None,
         sys.argv[3] if len(sys.argv) > 3 else None)
