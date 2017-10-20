# This is code to grab real time meteorological observation data from stations found at https://www.weatherlink.com/map.php
# Lat Lon bounds can be adjusted to choose areas of interest.
# Note code was created for grabbing data in Puget Sound, possible that other units for served data exists, which may cause errors in code but is easy to fix
# Code outputs a .csv of the data for each station and a metadata file with more information about each station.
# Takes roughly a minute to finish the data mining
# N. VanArendonk

import requests
from bs4 import BeautifulSoup
import re
import urllib
import json
from datetime import datetime
import time
#import pandas as pd

import send_email_text


# Run scrubber on all stations and save
def run_scrub():
    # Start timer
    start_time = time.time()
    
    # Lat Lon bounds of Salish Sea
    lon_bounds = [-125.60, -121.60]
    lat_bounds = [46.80, 50.40]
    
    # Determine current time 
    now = datetime.utcnow()
    
    # Data storage folder
    fol_name = '../Data/downloads/davis_winds/'
    
    # File name
    file_name = 'davisPS_{:s}'.format(now.strftime('%Y%m%d_%H%M'))
    
    # Read url of all the weatherlink stations and grab import to a variable
    # Does not always work the first time, 6 attempts are made
    url = 'https://www.weatherlink.com/mapstations.json?'
    try:    
        response = urllib.urlopen(url)
        data = json.loads(response.read())        
    except:
        for i in range(5):
            time.sleep(.1)
            try: 
                response = urllib.urlopen(url)
                data = json.loads(response.read())  
                msg = 'success'
                break
            except:
                msg = 'fail'
        if msg == 'fail':
            alert = 'Could not open station list after several attempts'
            send_email_text.send_email('schcrosby@gmail.com',alert)
            raise Exception(alert)
    
    # Grab all of the stations within the bounds and add to a separate list
    url_data = [] # Libraries to house data
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
    with open(fol_name+file_name, 'w') as f:
        # Write the header first
        f.writelines('Station,Lat,Lon,Wind_Speed,Wind_Direction, SLP, Time\n')
        for j in range(0, len(url_data)):
            # Combine the two dictionaries into one
            name = url_data[j]['uname']
            try: 
                cur_data = weatherlink_scrubber(name)
            except:
                alert = 'weatherlink_scrubber failed on station {:s}'.format(name)
                send_email_text.send_email('schcrosby@gmail.com',alert)
                raise Exception(alert)
            temp_dict = url_data[j].copy()
            temp_dict.update(cur_data)
            # Find keys in dictionary
            keys = temp_dict.keys()
            # Write the data to CSV file
            f.writelines('{},{},{},{},{},{},{}\n'
                         .format(temp_dict[keys[3]], temp_dict[keys[5]],
                                 temp_dict[keys[2]], temp_dict[keys[7]],
                                 temp_dict[keys[1]], temp_dict[keys[6]], temp_dict[keys[4]]))
    f.close()

    # End timer
    print 'Davis scrub complete, time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))


# Use to create meta list of stations and long names
def write_meta_data():
    
    # Lat Lon bounds of Salish Sea
    lon_bounds = [-125.60, -121.60]
    lat_bounds = [46.80, 50.40]
      
    # Read url of all the weatherlink stations and grab import to a variable
    url = 'https://www.weatherlink.com/mapstations.json?noCache=13'
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    
    # Grab all of the stations within the bounds and add to a separate list
    url_data = [] # Libraries to house data
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
            
    # Write metadata file for stations
    fname = 'davis_stations_meta.csv'
    # Create metadata file if it doesn't exist  
    with open(fname, 'w') as f:
        # Write the header
        f.writelines('Station Name,Station Description,Lat,Lon\n')
        for line in url_data:
            keys = line.keys()
            line[keys[2]] = line[keys[2]].replace(',', '')
            f.writelines('{},{},{},{}\n'.format(line[keys[1]], line[keys[2]], line[keys[0]], line[keys[3]]))
    f.close()
    print('Metadata File Created')


# Get's met data for a given station 
def weatherlink_scrubber(station_name):
    name = station_name.lower()
    name = name.replace(" ", "")

    ############# Build URL and access page/data #############
    link1 = 'http://www.weatherlink.com/user/'
    link2 = '/index.php?view=summary&headers=0'
    link = link1 + name + link2
    page = requests.get(link)

    #Now I parse the html code using the super handy BeautifulSoup function
    soup = BeautifulSoup(page.content, 'html.parser')

    # Create Dictionary to house all the key and values
    data = {}

    # Find all of the locations of the Meterological data within the HTML table
    search_params = ['Barometer', 'Wind Speed', 'Wind Direction']
    inds = []
    td_list = soup.findAll('td')
    i = 0
    for val in td_list:
        if val.get_text() in search_params:
            ind = i
            inds.append(ind)
        i += 1

    ########################## Grab the SLP ##########################
    slp = td_list[inds[0]+1].get_text()
    if slp == 'n/a':
        slp = '9999.99'
    slp_units = slp[-3:]
    slp_val = float(re.findall(r'[\d.]*\d+', slp)[0])

    # Assess units of served pressure data
    if 'mb' in slp_units:
        slp_convert = 0
    elif 'mm' in slp_units:
        slp_convert = 1
    elif 'hPa' in slp_units:
        slp_convert = 0
    elif slp == '9999.99':
        slp_convert = 0
    else:  # otherwise in inches of mercury
        slp_convert = 2

    # Create key for dictionary
    slp_key = 'slp'

    # Convert to metric if needed
    if slp_convert == 2:
        slp_val = slp_val * 33.8639
        slp_val = "%.2f" % slp_val
        slp_val = float(slp_val)
    elif slp_convert == 1:
        slp_val = slp_val * 1.33322
        slp_val = "%.2f" % slp_val
        slp_val = float(slp_val)

    # Update to dictionary
    data.update({slp_key: slp_val})

    # Throw error if 'weird' values are found
    if slp_val in range(2000, 9999) or slp_val < 800:
        print('Error with Pressure, possibly units: %s' % station_name)

    ########################## Grab the Wind Speed ##########################
    spd = td_list[inds[1]+1].get_text()

    # If speed is not served as a number but as calm convert to zero
    if spd == 'Calm':
        spd = '0'
    elif spd == 'n/a':
        spd = '999.99'

    # Assess units of served data for windspeed
    if 'KT' in spd[2:]: # units are in knots
        unit_compare = 1
    elif 'mph' in spd[2:] or 'Mph' in spd[2:] or 'MPH' in spd[2:]:
        unit_compare = 2
    else: # units are in
        unit_compare = 0

    # Create key for dictionary
    spd_key = 'spd'

    # Get just the Speed integer
    spd_str = re.findall(r'\d+', spd)
    spd_val = spd_str[0]
    spd_val = int(spd_val)

    # Convert to Metic
    if unit_compare == 1: # Convert from Knots to m/s
        spd_val = spd_val * 0.514444
        spd_val = "%.2f" % spd_val
        spd_val = float(spd_val)
    elif unit_compare == 2: # Convert from mph to m/s
        spd_val = spd_val * 0.44704
        spd_val = "%.2f" % spd_val
        spd_val = float(spd_val)

    # Put Speed as 999.99 if a n/a is served, after unit conversions
    if spd_val >= 999:
        spd_val = 999.99
    # Update to dictionary
    data.update({spd_key: spd_val})

    # Error catcher for possibly wrong data
    if spd_val < 0 or spd_val > 90 and spd_val < 999:
        print('Error with speed value, possibly units: %s' % station_name)

    ########################## Grab the Wind Direction ##########################
    wnddir = td_list[inds[2]+1].get_text()
    if wnddir == 'n/a':
        wnddir = '999'

    # Create key for dictionary
    wnddir_key = 'wnddir'

    # Get just the wind direction integer
    wnddir_lst = re.findall(r'\d+', wnddir)
    wnddir_val = wnddir_lst[0]
    wnddir_val = int(wnddir_val)

    # Update to dictionary
    data.update({wnddir_key: wnddir_val})

    # Error catcher for bad wind direction
    if wnddir_val > 360 and wnddir_val != 999:
        print('Error with wind direction: %s' % station_name)

    ########################## Grab the Time ##########################
    now = datetime.utcnow()
    cur_date = '%d/%d/%d %d:%d:%d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    time_key = 'time'
    data.update({time_key: cur_date})

    # Set data dictionary as global variable
    return(data)


# Test Case
#data = weatherlink_scrubber('nskabb')
#print(data)


# Runs Main Script if used as stand-alone     
if __name__ == '__main__':        
    try:    
        run_scrub()
    except:
        alert = 'run_scrub() failed for unknown reason'
        send_email_text.send_email('schcrosby@gmail.com',alert)
        raise Exception(alert)
    
    






