import os
from datetime import datetime, timedelta

FormatZ = '%Y-%m-%d %H:%M:%S %Z'

def find_latest_canadian_data(gribPrefix):
    #gribPrefix = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_'
    #daysOffset = 0
    found = False
    for ndy in [0,-1]:
        NowUTC = datetime.utcnow() + timedelta(days=ndy)
        dateString = NowUTC.strftime('%Y%m%d')
        print('UTC time: {0:s}'.format(NowUTC.strftime(FormatZ)))
        # Check for 48 hour forecast and set value of utc.
        forecastHr = 48
        for runStart in [18,12,6,0]:
            gribName = '{0:s}{1:s}{2:02d}_P{3:03d}-00.grib2'.format(gribPrefix, dateString, runStart, forecastHr)
            gribUrl   = 'http://dd.weather.gc.ca/model_hrdps/west/grib2/{0:02d}/{1:03d}/{2:s}'.format(runStart, forecastHr, gribName)
            print(gribUrl)
            print(gribName)
            command = "curl -f -s {0:s} -o {1:s}".format(gribUrl, 'local.idx')
            err = os.system(command)
            #command  = ['wget','-q','--spider',gribUrl]
            #checkUrl = subprocess.call(command, shell=True) # check_call() would stop the program, check() allows the loop to continue.
            #print(checkUrl)
            if err != 0:
                print('48 hour file doesn\'t exist yet for {0:s}, {1:02d}Z'.format(dateString, runStart)),
                print(' Trying earlier time.')
            if err == 0:
                utc = runStart
                #daysOffset = ndy
                found = True
                break   # break out of runStart loop
        if found:
            break   # break out of ndy loop
    return dateString, utc

    # If there is no internet connection, fill in the date below and comment out active code above.
    #return datetime.strptime('2016-01-02 12:00', "%Y-%m-%d %H:%M"), 12
def fetch_canadian(gribPrefix, dateString, dateStringCanada, utcCanada):
    fileCount = 48
    folder = 'CANADA/downloaded_canadian_grib_files/downloaded_canadian_grib_files_{0:s}/'.format(dateString)
    if os.path.exists(folder):
        print('Folder \'{0:s}\' exists.'.format(folder))
    else:
        os.mkdir('CANADA/downloaded_canadian_grib_files/downloaded_canadian_grib_files_{0:s}'.format(dateString))
    #for utm in [0,12]:    # Note that on one occasion 12z forecast data was not all posted at nomads until 10:00 a.m.
    for Hour in range(fileCount):
        gribName = '{0:s}{1:s}{2:02d}_P{3:03d}-00.grib2'.format(gribPrefix, dateStringCanada, utcCanada, Hour)
        gribUrl = 'http://dd.weather.gc.ca/model_hrdps/west/grib2/{0:02d}/{1:03d}/{2:s}'.format(utcCanada, Hour, gribName)
        print(folder + gribName),
        if not os.path.isfile(folder + gribName):
            #fileName = 'local.idx'
            #command = "curl -f -v -s {0:s} -o {1:s}".format(idxUrl, fileName)  # verbose version
            command = "curl -f -s {0:s} -o {1:s}".format(gribUrl, folder+gribName)
            err = os.system(command)
            #command = "curl -f -s -r {0:s} {1:s} -o {2:s}".format(Range, url, folder+gribName)
            #err = os.system(command)
            print('error {0:d}'.format(err))
            if err != 0:
                return Hour
        else:
            print(' found')
    return fileCount