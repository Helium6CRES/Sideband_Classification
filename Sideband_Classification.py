"""
File takes path to clustered He-6 CRES experimental data, axial_frequency
minimums for each field, axial frequency maximums for each field, and a number
of poitns to check for each event. File will classify every event in the file
as a band type, gives each band set a unique beta count, and records its axial
frequency. File saves a CSV "Data_with_sidebands.csv" which represents the
input CSV with additional columns for band type, beta number, and axial frequency.
"""


import pandas as pd
import numpy as np
import time
import os

# Data input
filepath = input("Absolute Data Path: ")
datafile = open(filepath)
df = pd.read_csv(datafile, sep=',')

# Appending other columns
df["Band_type"] = 2
df["Beta"] = 0
df["Axial_Frequency"] = 0

fields = sorted(df["set_field"].unique())

print("Input frequency ranges for the detected fields", fields)

# Axial frequency range input
fA_min_input = input("Minimum Axial Frequencies in MHz (integers seperated by spaces): ")
fA_min = []
for value in fA_min_input.split():
    fA_min.append(int(value) * (10 ** 6))

fA_max_input = input("Maximum Axial Frequencies in MHz (integers seperated by spaces): ")
fA_max = []
for value in fA_max_input.split():
    fA_max.append(int(value) * (10 ** 6))

axial_frequencies = list(zip(fA_min, fA_max))

points_per_event = int(input("Number of points per track to check: "))

tic = time.perf_counter()

default_tolerance = 0.05

print()
length = len(df)
print("Events to classify:", length)


cols = ['run_id', 'file_id']
df['UniGID'] = df[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)

total_len = len(df)
by_field = df.groupby("set_field")


def approx_equal(arg1, arg2):
    """
    A Helper function that two arguments and returns a boolean if they are
    within a percentage of each other, defined by the default_tolerance variable
    """

    if arg1 >= (1 + default_tolerance) * arg2:
        return False
    elif arg2 >= (1 + default_tolerance) * arg1:
        return False
    return True


def event_lines(n, start, end):
    """
    Function takes a starting and ending point of (x, y) tuples and an integer
    n. Function then returns a list of n points equally spaced along the line
    defined by the start and end inputs, not including points that would lie
    on top of the start or end positions.
    """
    x_gap = (end[0] - start[0]) / (n + 1)
    y_gap = (end[1] - start[1]) / (n + 1)
    points = []

    for point in range(n + 2):
        points.append(((start[0] + (x_gap * point)), (start[1] + (y_gap * point))))

    return points


def is_between(start, end, points, slope):
    """
    Function takes the tuples start and end: each tuples describing the start
    and end of a line segment, points: a pair of tuples defining 2 points
    seperated only vertically, and slope: the slope of the line dfined by
    start and end. Function determines if a point on the line between start
    and end lies between the pair of points and returns the corresponding boolean.
    """
    point_on_line = slope * (points[0][0] - start[0]) + start[1]
    if point_on_line > end[1]:
        return False
    elif point_on_line >= points[0][1] and point_on_line <= points[1][1]:
        return True
    return False


def assemble_points(x, y, y_gap_range):
    """
    Function takes x and y: integers representing a point in space and y_gap_range:
    a tuple describing the range from the y coordinate to be calculated.
    The function assembles a pair of y values describing a range one multiple
    of y_gap_range above the y input, two mutiples above, one multiple below, and
    two multiples below the y input. The function returns 4 lists, each of 2 tuples
    with each list corresponding to its own range.
    """
    close_above = [(x, y + y_gap_range[0]), (x, y + y_gap_range[1])]
    close_below = [(x, y - y_gap_range[1]), (x, y - y_gap_range[0])]
    far_above = [(x, y + (2 * y_gap_range[0])), (x, y + (2 * y_gap_range[1]))]
    far_below = [(x, y - (2 * y_gap_range[1])), (x, y - (2 * y_gap_range[0]))]
    return close_above, close_below, far_above, far_below


def main_axial_frequency(mainband, above_band, below_band):
    """
    The function takes 3 arguments, each being rows of the main dataframe.
    These represent what has been found to be a mainband and 2 adjacent sidebands.
    The function takes the start and end times of the mainband and upper sideband
    and takes finds the difference of the y coordinates at the middle of those
    times. The function does the same with the mainband and the lower sideband
    and averages the 2 found values and returns it, representing the axial
    frequency of the mainband-sideband set.
    """
    numbers = [above_band["EventStartTime"], above_band["EventEndTime"], mainband["EventStartTime"], mainband["EventEndTime"]]
    ordered = sorted(numbers)
    x = ordered[1]
    higher_freq = above_band["EventSlope"] * (x - above_band["EventStartTime"]) + above_band["EventStartFreq"]
    main_freq = mainband["EventSlope"] * (x - mainband["EventStartTime"]) + mainband["EventStartFreq"]
    upper_axial_freq = higher_freq - main_freq
    numbers = [below_band["EventStartTime"], below_band["EventEndTime"], mainband["EventStartTime"], mainband["EventEndTime"]]
    ordered = sorted(numbers)
    x = ordered[1]
    lower_freq = below_band["EventSlope"] * (x - below_band["EventStartTime"]) + above_band["EventStartFreq"]
    main_freq = mainband["EventSlope"] * (x - mainband["EventStartTime"]) + mainband["EventStartFreq"]
    lower_axial_freq = abs(main_freq - lower_freq)
    axial_frequency = np.average([upper_axial_freq, lower_axial_freq])
    return abs(axial_frequency)


def side_axial_frequency(above_band, below_band, point):
    """
    This function takes 2 inputs, above_band and below_band, each
    corresponding to rows of the larger dataframe, specifically 2
    events that have been found to be a pair of sidebands lacking a mainband.
    Function calculates the vertical distance between these bands and returns
    the absolute value of the difference divided by two, representing the
    axial frequency of the pair.
    """
    numbers = [above_band["EventStartTime"], above_band["EventEndTime"], below_band["EventStartTime"], below_band["EventEndTime"]]
    x = point[0]
    freq_top = above_band["EventSlope"] * (x - above_band["EventStartTime"]) + above_band["EventStartFreq"]
    freq_bottom = below_band["EventSlope"] * (x - below_band["EventStartTime"]) + below_band["EventStartFreq"]
    axial_frequency = (freq_top - freq_bottom) / 2
    return abs(axial_frequency)


# Various counters:
# event_count increments with every new event and records how many events have
# been looped through for the sake of recording progress
event_count = 0
# range_index records which axial frequency range to use for the given field
range_index = -1

# Percent interval to display progress
display_interval = 5
# Counter to only display progress once every 5%
progress_counter = 0


"""
Main loop. Code loops through each field of the data. The field then loops
through each unique run_id/file_id combination within that field. It then
loops through each event within that unique id and assembles a number of
equidistant points along it, determined by the user input. It then calls
assemble_points to make 4 axial_frequency ranges for each of these points.
It then checks every other event within the unique ID to find if any events
lie within any of the ranges, and classifies both events based on where the
other events lie. It will then give the mainband or sideband a number that is
either unique or corresponds to a set of events that are part of the same
mainband-sideband-sideband or sideband-sideband set. It then calculates an
axial frequency of the set, recording a zero for lone bands.
"""
for k, field in by_field:
    range_index += 1
    axial_freq_range = axial_frequencies[range_index]
    gdf = field.groupby("UniGID")
    for j, group in gdf:
        for index, event in group.iterrows():
            # Progress report
            event_count += 1
            progress_percent = 100 * event_count / total_len

            if progress_percent >= progress_counter * display_interval:
                print(f"Progress: {round(progress_percent)}%")
                progress_counter += 1

            beta = df.at[index, "Beta"]

            # Gives event a unique beta, if it doesn't already belong to a set of bands
            if beta == 0:
                df.at[index, "Beta"] = index
                beta = index

            event_start = [event["EventStartTime"], event["EventStartFreq"]]
            event_end = [event["EventEndTime"], event['EventEndFreq']]

            immediately_above = []
            immediately_below = []
            is_above = False
            is_below = False
            band = df.at[index, "Band_type"]

            # Skip event if already classified as a sideband
            if band == 1 or band == -1:
                continue

            # Assemble equidistant points along the track
            points = event_lines(points_per_event, [event["EventStartTime"], event["EventStartFreq"]], [event["EventEndTime"], event["EventEndFreq"]])
            for point in points:
                if point == points[0] or point == points[-1]:
                    continue

                # Assemble axial frequency ranges
                close_above, close_below, far_above, far_below = assemble_points(point[0], point[1], axial_freq_range)

                for i, other_event in group.iterrows():
                    slope = other_event["EventSlope"]
                    curr_event_start = [other_event["EventStartTime"], other_event["EventStartFreq"]]
                    curr_event_end = [other_event["EventEndTime"], other_event["EventEndFreq"]]

                    # Checks that the other_event is not the parent event
                    if i == index:
                        continue

                    # Checks that the other_event has a similar slope to the parent_event
                    if not approx_equal(slope, event["EventSlope"]):
                        continue

                    # Far below band check
                    elif is_between(curr_event_start, curr_event_end, far_below, slope):
                        if other_event["Band_type"] == 2:
                            df.at[i, "Beta"] = beta
                        else:
                            df.at[index, "Beta"] == other_event["Beta"]
                        axial_freq = side_axial_frequency(event, other_event, point)
                        df.at[i, "Band_type"] = -1
                        df.at[i, "Axial_Frequency"] = axial_freq
                        df.at[index, "Axial_Frequency"] = axial_freq
                        df.at[index, "Band_type"] = 1
                        continue

                    # Far above band check
                    elif is_between(curr_event_start, curr_event_end, far_above, slope):
                        if other_event["Band_type"] == 2:
                            df.at[i, "Beta"] = beta
                        else:
                            df.at[index, "Beta"] == other_event["Beta"]
                        axial_freq = side_axial_frequency(event, other_event, point)
                        df.at[i, "Band_type"] = 1
                        df.at[index, "Band_type"] = -1
                        df.at[i, "Axial_Frequency"] = axial_freq
                        df.at[index, "Axial_Frequency"] = axial_freq
                        continue

                    # Adjacent above band check
                    elif is_between(curr_event_start, curr_event_end, close_above, slope):
                        immediately_above.append(i)
                        is_above = True

                    # Adjacent below band check
                    elif is_between(curr_event_start, curr_event_end, close_below, slope):
                        immediately_below.append(i)
                        is_below = True

                    # Accompanied mainband check
                    if is_below and is_above:
                        axial_freq = main_axial_frequency(event, df.loc[immediately_above[0]], df.loc[immediately_below[0]])
                        for above in immediately_above:
                            df.at[above, "Beta"] = beta
                            df.at[above, "Band_type"] = 1
                            df.at[above, "Axial_Frequency"] = axial_freq
                        for below in immediately_below:
                            df.at[below, "Beta"] = beta
                            df.at[below, "Band_type"] = -1
                            df.at[below, "Axial_Frequency"] = axial_freq
                        df.at[index, "Band_type"] = 0
                        df.at[index, "Axial_Frequency"] = axial_freq


toc = time.perf_counter()
time_elapsed = toc - tic
print("Time Elapsed:", time_elapsed // 60, "Minutes", time_elapsed % 60, "Seconds")

suffix = "_with_sidebands"
directory = os.path.dirname(filepath)
filename, extension = os.path.splitext(os.path.basename(filepath))
new_filename = f"{filename}{suffix}{extension}"
path = os.path.join(directory, new_filename)
df.to_csv(path)

print()
print("Mainbands:", len(df[df["Band_type"] == 0]))
print("Lone Mainbands:", len(df[df["Band_type"] == 2]))
print("Lone Mainband Fraction of Tracks:", len(df[df["Band_type"] == 2]) / len(df))
print("Lower Bands:", len(df[df["Band_type"] == -1]))
print("Upper Bands:", len(df[df["Band_type"] == 1]))
