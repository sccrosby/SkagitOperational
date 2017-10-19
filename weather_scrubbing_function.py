# Get Station Data from Weatherlink Stations

import requests
from bs4 import BeautifulSoup
import re
import datetime


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
    slp_len = len(slp)
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
    now = datetime.datetime.now()
    cur_date = '%d/%d/%d %d:%d:%d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    time_key = 'time'
    data.update({time_key: cur_date})

    # Set data dictionary as global variable
    return(data)


# Test Case
#data = weatherlink_scrubber('nskabb')
#print(data)









