# -*- coding: utf-8 -*-

"""
A practice toolset for studying earthquake trends.

Makes use of data from the Earthquake Catalog API at the USGS Earthquake Hazard
Program: http://earthquake.usgs.gov/earthquakes/search/

Meta-study on precursor earthquakes occurring before strong earthquakes:
http://www.nature.com/articles/srep04099

The data used in this script are provided in the git repo. The script to 
download them from the online USGS database is included as well.

Usage (with my_path giving the location where data are saved): 
- When calling from the terminal (0 for plotting data, 1 for downloading/saving), 
>>> python trends.py my_path 0

- When calling from the python shell: 
>>> import trends
>>> trends.fn_base = 'my_path'
>>> data = trends.saveMainEvents()
>>> dprec_total = trends.savePrecursorEvents(data)
>>> plotEQHistory(dprec_total)
>>> plotSomething()

Author: R. Lombaert

"""

import matplotlib.pyplot as plt
import pandas as pd
import os, sys, time
import numpy as np

global fn_base

import matplotlib
matplotlib.style.use('ggplot')


def retrieveData(parse_dates=0,**kwargs):

    '''
    Retrieve data from the Earthquake Catalog API at the USGS Earthquake Hazard
    Program and save to disk: http://earthquake.usgs.gov/earthquakes/search/
    
    Any additional kwargs are added to the url for the query to the USGS 
    database. 
    
    @keyword parse_dates: Parse the time strings as pd.Timestamp in given 
                          columns. Default if no timestamp parsing is to be done
                          
                          (default: False)
    @type parse_dates: list[int]
    
    @return: The data as retrieved following the parameters set in kwargs
    @rtype: pd.DataFrame
    
    '''
    
    if not kwargs: 
        print('No query arguments specified.')
        return
    url = 'http://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&'
    url += '&'.join(['='.join([k,str(v)]) for k,v in kwargs.items()])
    print('Retrieving data from:')
    print(url)
    print('--------------')
    while True: 
        try:
            data = pd.read_csv(url,parse_dates=parse_dates)
            break
        except:
            print('URLError... Waiting 60 seconds and trying again.')
            time.sleep(60)
    
    return data



def saveMainEvents():
    
    '''
    Save the list of main events to a file.
    
    Data are extracted via the Earthquake Catalog API at the USGS Earthquake 
    Hazards Program: http://earthquake.usgs.gov/earthquakes/search/
    
    For now limited to all earthquakes since 1900 above magnitude 6.
    
    For more information on the magnitude scale:
    http://www.geo.mtu.edu/UPSeis/magnitude.html
    
    @keyword fn_base: The base filepath for the data.
    
                      (default: "~/TDI/project_prop/EarthquakeTrends/data/")
    @type fn_base: str
    
    @return: The data for the main events since 1900 above magnitude 6
    @rtype: pd.DataFrame
    
    '''
    
    #-- Data download and save as of October 27th, 2016
    kwargs = {'starttime':'1900-01-01','endtime':'2016-11-01',\
              'eventtype':'earthquake','minmagnitude':6}

    #-- retrieveData creates the API url used by pandas to retrieve data.
    data = retrieveData(parse_dates=[0,12],**kwargs)

    #-- Save the data containing the main events
    fn = os.path.join(fn_base,'strongEQ_USGS.csv')
    data.to_csv(fn,index=0)
    
    return data
    
    

def savePrecursorEvents(data):

    '''
    Save the list of the precursor events to files based on a set of main 
    events.
    
    Data are extracted via the Earthquake Catalog API at the USGS Earthquake 
    Hazards Program: http://earthquake.usgs.gov/earthquakes/search/
    
    For now limited to a search centred on the main event within a radius of 100
    km and up to one year before the main event.
    
    For more information on the magnitude scale:
    http://www.geo.mtu.edu/UPSeis/magnitude.html
    
    @param data: The data for the main events
    @type data: pd.DataFrame

    @return: The data for the precursor events
    @rtype: pd.DataFrame
    
    '''
    
    #-- To retrieve the precursor earthquakes to each main event, loop over the 
    #   events and select all precursors
    for line in data.itertuples():
        fn = os.path.join(fn_base,'strongEQ_prec_{}_USGS.csv'.format(line[0]))
    
        #-- Some redundancy in case the code stopped.
        if os.path.isfile(fn): continue
        
        #-- The time format
        tfmt = '%Y-%m-%dT%H:%M:%S'
        
        #-- Make sure the start time is not before 1900 (DateOffset isn't happy
        #   about the 19th century)
        try:
            start = (line.time - pd.DateOffset(years=1)).strftime(tfmt)
        except ValueError: 
            start = line.time.strftime(tfmt).replace('1900','1899')
        
        #-- Set the end time 1 second after the main event so it is included.
        end = (line.time + pd.DateOffset(seconds=1)).strftime(tfmt)
    
        #-- Retrieve the data
        kwargs = {'starttime': start, 
                  'endtime': end,
                  'eventtype': 'earthquake',
                  'minmagnitude': 1.0,
                  'longitude': line.longitude,
                  'latitude': line.latitude,
                  'maxradiuskm': 100}
        dprec = retrieveData(parse_dates=[0,12],**kwargs)
    
        #-- Add an additional column linking the precursors with the main event by 
        #   its index in the main data. Note that the main event is typically the 
        #   first event in the list of precursors for the event index.
        dprec['main_event'] = pd.Series([line[0]]*len(dprec.time),index=dprec.index)
    
        #-- Save the precursor dataset to merge it later 
        fn = os.path.join(fn_base,'strongEQ_prec_{}_USGS.csv'.format(line[0]))
        dprec.to_csv(fn,index=0)
    
        #-- Let's play nice on the API and maintain a maximum of one query per 
        #   second
        time.sleep(1)

    #-- Once downloaded, read all the files again and save to one main database.
    all = []
    for line in data.itertuples():
        fn = os.path.join(fn_base,'strongEQ_prec_{}_USGS.csv'.format(line[0]))
        dprec = pd.read_csv(fn,parse_dates=[0,12])
    
        #-- Make sure the indices play nice in case we use the dprec_total DF as
        #   is
        dprec.index = dprec.index + len(all[-1].index) if all else dprec.index
        all.append(dprec)

    #-- Merge the DFs together and save.
    dprec_total = pd.concat(all)
    fn = os.path.join(fn_base,'strongEQ_precursors_USGS.csv')
    dprec_total.to_csv(fn,index=0)
    
    return dprec_total



def plotEQHistory(): 

    '''
    Plot the earthquake magnitude as a function of time for all main and 
    precursor events.
    
    '''

    fn = os.path.join(fn_base,'strongEQ_precursors_USGS.csv')
    df = pd.read_csv(fn,usecols=['time','mag'],parse_dates=[0])
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot_date(x=df.time, y=df.mag, marker='.', ms=2)
    plt.xlabel('Date of event')
    plt.ylabel('Earthquake Magnitude')
    plt.show()
    pfn = os.path.join(fn_base,'plotEQMagHistory.png')
    fig.savefig(pfn)
    


def plotEQFrequency():

    '''
    Plot the micro earthquake event frequency  as a function of time.
    
    A micro event is defined as an earthquake having magnitude less than the 
    main event minus 3. 
    
    '''
    
    fn = os.path.join(fn_base,'strongEQ_precursors_USGS.csv')
    df = pd.read_csv(fn,usecols=['time','mag','main_event'],parse_dates=[0])
    df.index = df.time
    df = df['1970':]
    df = df[df.mag < (df.groupby('main_event').mag.max().get(df['main_event']) - 3)]
    df = df[df.groupby('main_event').main_event.count().get(df.main_event).values>2000]
    dfg = df.groupby('main_event')
    print np.unique(df.main_event.values)
    df['days_before'] = (df.time-(dfg.time.max().get(df.main_event)-pd.DateOffset(years=1)).values)/np.timedelta64(1,'D')
    df['freq_prec'] = (dfg.main_event.cumcount(ascending=False)+1)/df.days_before
    
    plt.clf()
    fig = plt.figure(1)
    
    for i,idf in df.groupby('main_event'):
        plt.plot(idf['days_before'].values,idf['freq_prec'].values)
        
    plt.xlabel('Time (days)')
    plt.ylabel('Micro-event frequency (1/days)')
    plt.ylim(ymax=25)
    plt.xlim(xmin=0)
    plt.xlim(xmax=366)
    plt.show()
    pfn = os.path.join(fn_base,'plotEQFrequency.png')
    fig.savefig(pfn)
    
    
    
if __name__ == "__main__":
    
    try:
        fn_base = sys.argv[1]
    except IndexError:
        fn_base = os.getcwd()
        
    try: 
        save_data = sys.argv[2]
    except IndexError:
        save_data = 0
        
    if int(save_data):    
        data = saveMainEvents()
        dprec_total = savePrecursorEvents(data)
    
    plotEQHistory()
    plotSomething()

