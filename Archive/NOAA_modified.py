i#mport urllib.request as urllib2 # debugging in Python 3
import urllib2
import re
from pytz import timezone
from datetime import datetime, timedelta
import os
# # # # # # # # # # # # # # # # 
def str2num(myString):
    if myString[-1] == '\n':
        return float(myString[:-1])
    else:
        return float(myString)
# # # # # # # # # # # # # # # #
def getTides(mllw2NAVD88, timeDifference):
    tide48hr = [None] * 48
    pattern = '<td nowrap width="25%" align="right" >'
    pdt = timezone('US/Pacific')
    for dayDiff in range(2):
        date = datetime.now(pdt) - timedelta(days=dayDiff)
        #NOAA = ('https://tidesandcurrents.noaa.gov/noaatidepredictions/viewDaily'+
        #    'Predictions.jsp?bmon='+
        #    '{0:02d}&bday={1:02d}&byear={2:04d}'.format(date.month, date.day, date.year) + 
        #    '&timelength=daily&timeZone=2' +
        #    '&dataUnits=0&datum=MLLW&timeUnits=1&interval=60&Threshold='+
        #    'greaterthanequal&thresholdvalue=&format=Submit&Stationid=9448576')
        NOAA = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=9448576&units=standard&bdate={0:04d}{1:02d}{2:02d}&edate=20170503&timezone=GMT&clock=12hour&datum=MLLW&interval=h&action=data'.format(date.year, date.month, date.day)
        #print(NOAA) #debugging in Python 3
        aResp = urllib2.urlopen(NOAA)
        web_pg = aResp.read()
        patternFound = [m.start() for m in re.finditer(pattern, web_pg)]
        result = [web_pg[m+len(pattern)+2:m+len(pattern)+6] for m in patternFound]
        resultInFloat = [str2num(m)+mllw2NAVD88 for m in result]
        if dayDiff == 0:
            tide48hr[7:] = resultInFloat[:41]
        elif dayDiff == 1:
            tide48hr[:7] = resultInFloat[41:]
    tideFolder = 'USA/Tide_data'
    if not os.path.exists(tideFolder):
        os.mkdir(tideFolder)
    dateString  = datetime.now(pdt).strftime('%Y%m%d')
    tideFile = '{0:s}/tide_forecast_{1:s}.txt'.format(tideFolder, dateString)
    fid = open(tideFile,'w')
    date = datetime.now(pdt) - timedelta(days=1)
    dateTemp = datetime(date.year, date.month, date.day, 17)
    for tideIndex in range(48):
        fid.write('{0:s}   {1:3.3f}\n'.format(dateTemp.strftime('%Y-%m-%d %H:%M:%S'), tide48hr[tideIndex]))
        dateTemp = dateTemp + timedelta(hours=1)
    fid.close()
    return tide48hr
    
    
def getTides_canada(mllw2NAVD88, timeDifference, dateStringCanada, utcCanada):
    #tide48hr = [None] * 48
    resultTwoDays = [None] * 96
    pattern = '<td nowrap width="25%" align="right" >'
    pdt = timezone('US/Pacific')
    for dayDiff in range(2):
        #date = datetime.now(pdt) - timedelta(days=dayDiff)
        date = datetime.strptime(dateStringCanada , '%Y%m%d') + timedelta(days=dayDiff)
        NOAA = ('https://tidesandcurrents.noaa.gov/noaatidepredictions/viewDaily'+
            'Predictions.jsp?bmon='+
            '{0:02d}&bday={1:02d}&byear={2:04d}'.format(date.month, date.day, date.year) + 
            '&timelength=daily&timeZone=0' +
            '&dataUnits=0&datum=MLLW&interval=60&Threshold='+
            'greaterthanequal&thresholdvalue=&format=Submit&Stationid=9448576')
        aResp = urllib2.urlopen(NOAA)
        web_pg = aResp.read()
        patternFound = [m.start() for m in re.finditer(pattern, web_pg)]
        result = [web_pg[m+len(pattern)+2:m+len(pattern)+6] for m in patternFound]
        resultInFloat = [str2num(m)+mllw2NAVD88 for m in result]
        resultTwoDays[dayDiff*48:(dayDiff+1)*48] = resultInFloat
    tide48hr = resultTwoDays[utcCanada:utcCanada+48]
    tideFolder = 'CANADA/Tide_data_canada'
    if not os.path.exists(tideFolder):
        os.mkdir(tideFolder)
    #dateString  = datetime.now(pdt).strftime('%Y%m%d')
    tideFile = '{0:s}/tide_forecast_{1:s}_{2:02d}Z.txt'.format(tideFolder, dateStringCanada, utcCanada)
    fid = open(tideFile,'w')
    date = datetime.now(pdt) - timedelta(days=1)
    dateTemp = datetime(date.year, date.month, date.day, 17)
    for hour in range(48):
        dateTemp = (datetime.strptime(dateStringCanada , '%Y%m%d') + timedelta(hours= utcCanada + hour - timeDifference)).strftime('%Y-%m-%d %H:%M:%S')
        fid.write('{0:s}   {1:3.3f}\n'.format(dateTemp, tide48hr[hour]))
    fid.close()
    latestTideFile = '{0:s}/latest_tide_time.txt'.format(tideFolder)
    fid = open(latestTideFile,'w')
    fid.write('{0:s}   {1:02d}'.format(dateStringCanada, utcCanada))
    fid.close()
    return tide48hr

