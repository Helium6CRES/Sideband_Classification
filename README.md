# sideband_classification


This code is intended to be used for the He-6 CRES experiment on experiment data that has already undergone clustering into individual tracks.

The Sideband_Classification file will take this data and append onto it columns that classify each track status as a mainband or sideband, numbers each set of bands as a unique beta, and the calculated axial frequency of the set of bands, if not alone.

The Axial_Hist_Plot file takes the output CSV from Sideband_Classification and creates a histogram of the axial frequencies for each field, neglecting all zeroes.



To use the code, Sideband_Classification requires a path to the clustered data, and expected frequency ranges for each of the fields included in the data, as well as a a number of points to check for each track.

1. Run the script 'Sideband_Classification'
2. Input absolute data path (no commas)
3. Input axial frequency minimums for each field (MHz, separated by spaces)
4. Input axial frequency maximums for each field (MHz, separated by spaces)
5. Input a number of points to check for each track

Note: Increasing the number of points to check will increase accuracy, but also runtime.

An example to demonstrate the usage of Sideband_Classification is as follows, where the quotes are the user input:

##
Absolute Data Path: "D:\Sidebands\events.csv"

Input frequency ranges for the detected fields [0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25]

Minimum Axial Frequencies in MHz (integers seperated by spaces): "51 80 93 99 102 106 105 109 109 110 110"

Maximum Axial Frequencies in MHz (integers seperated by spaces): "67 98 117 122 125 128 129 129 131 131 131"

Number of points per track to check: "5"
##

The code will then store a file in the same location as the input with the addition of the suffix "_with_sidebands" appended, which represents the experimental data with further columns describing the band type (Top band, bottom band, mainband, lone band), the beta the band belongs to, and the axial frequency of the band.



Axial_Hist_Plot requires a filepath to the sideband-processed CSV
To plot:

1. Run 'Axial_Hist_Plot'
2. Input filepath of CSV output by Sideband_Classification when prompted

Example where quotes represent user input:

##
Input sideband-processed data path: "C:\Users\blake\Data_with_sidebands.csv"
##

The file will then display a collection of histograms for the axial frequency of each field, which can then be saved.
