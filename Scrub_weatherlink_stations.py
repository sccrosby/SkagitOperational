import urllib
import json
import os.path
from weather_scrubbing_function import weatherlink_scrubber
import pandas as pd

# This is code to grab real time meteorological observation data from stations found at https://www.weatherlink.com/map.php
# Lat Lon bounds can be adjusted to choose areas of interest.
# Note code was created for grabbing data in Puget Sound, possible that other units for served data exists, which may cause errors in code but is easy to fix
# Code outputs a .csv of the data for each station and a metadata file with more information about each station.
# Takes roughly a minute to finish the data mining



# Read url of all the weatherlink stations and grab import to a variable
url = 'https://www.weatherlink.com/mapstations.json?noCache=13'
response = urllib.urlopen(url)
data = json.loads(response.read())



# Lat Lon bounds of Salish Sea
lon_bounds = [-125.60, -121.60]
lat_bounds = [46.80, 50.40]

# Libraries to house data
url_data = []


# Grab all of the stations within the bounds and add to a separate list
for j in range(0, len(data)):
    if data[j]['lat'] >= lat_bounds[0] and data[j]['lat'] <= lat_bounds[1] and data[j]['lng'] >= lon_bounds[0] and data[j]['lng'] <= lon_bounds[1]:
        info = {
            "sname": data[j]['sname'].encode('utf8'),  # Encode from unicode to string
            "uname": data[j]['uname'].encode('utf8'),  # Encode from unicode to string
            "lat":   '%.4f' % data[j]['lat'],
            "lon":   '%.4f' % data[j]['lng']
        }
        url_data.append(info)
        #names.append(data[j]['uname'])

# Create csv file and write data to it
with open('test.csv', 'w') as f:
    # Write the header first
    f.writelines('Station Name,Lat,Lon,Wind Speed,Wind Direction, Sea Level Pressure, Time\n')
    for j in range(0, len(url_data)):
        # Combine the two dictionaries into one
        name = url_data[j]['uname']
        cur_data = weatherlink_scrubber(name)
        temp_dict = url_data[j].copy()
        temp_dict.update(cur_data)
        # Find keys in dictionary
        keys = temp_dict.keys()
        # Write the data to CSV file
        f.writelines('{},{},{},{},{},{},{}\n'
                     .format(temp_dict[keys[3]], temp_dict[keys[5]],
                             temp_dict[keys[2]], temp_dict[keys[7]],
                             temp_dict[keys[1]], temp_dict[keys[6]], temp_dict[keys[4]]))
print('Data file created')
f.close()

# Write metadata file for stations
fname = 'metadata.csv'
# Create metadata file if it doesn't exist
if not os.path.isfile(fname):
    with open(fname, 'w') as f:
        # Write the header
        f.writelines('Station Name,Station Description,Lat,Lon\n')
        for line in url_data:
            keys = line.keys()
            line[keys[2]] = line[keys[2]].replace(',', '')
            f.writelines('{},{},{},{}\n'.format(line[keys[1]], line[keys[2]], line[keys[0]], line[keys[3]]))
    f.close()
    print('Metadata File Created')


# Create a pandas dataframe from the CSV file of the
df = pd.read_csv(fname, header=0, sep=',')


