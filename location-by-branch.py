import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
import json
import time

class LocationBrancher():
    """docstring for LocationBrancher."""

    df_gps= None
    date_range=None


    def __init__(self):
        self.__loadHistory()
        self.__convertData()

        for x in range(0,len(self.df_gps['datetime'].keys() ) ):
            if(-1 != int(self.df_gps['alt'][x]) ):
                print("Alt: "+str(self.df_gps['alt'][x]))
                print("Location: "+str(self.df_gps['lat'][x])+", "+str(self.df_gps['lon'][x]))
                print("Time: "+str(str(self.df_gps['datetime'][x])))
                print("")

    def __loadHistory(self):
        # load the full location history json file downloaded from google
        self.df_gps = pd.read_json('data/location_history.json')
        print("Rows of Data: "+str(len(self.df_gps)))

    def __fillAltitude(self, loc):
        if('altitude' in loc.keys()):
            return loc['altitude']
        else:
            return -1

    def getDataFrame(self):
        return self.df_gps

    def __convertData(self):
        # parse lat, lon, alt, and timestamp from the dict inside the locations column

        self.df_gps['alt'] = self.df_gps['locations'].map(lambda x: self.__fillAltitude(x))
        self.df_gps['lon'] = self.df_gps['locations'].map(lambda x: x['longitudeE7'])
        self.df_gps['lat'] = self.df_gps['locations'].map(lambda x: x['latitudeE7'])
        self.df_gps['timestamp_ms'] = self.df_gps['locations'].map(lambda x: x['timestampMs'])

        # convert lat/lon to decimalized degrees and the timestamp to date-time
        self.df_gps['lat'] = self.df_gps['lat'] / 10.**7
        self.df_gps['lon'] = self.df_gps['lon'] / 10.**7
        self.df_gps['timestamp_ms'] = self.df_gps['timestamp_ms'].astype(float) / 1000
        self.df_gps['datetime'] = self.df_gps['timestamp_ms'].map(lambda x: dt.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
        self.date_range = '{}-{}'.format(self.df_gps['datetime'].min()[:4], self.df_gps['datetime'].max()[:4])

        self.df_gps = self.df_gps.drop(labels=['locations', 'timestamp_ms'], axis=1, inplace=False)

if __name__ == '__main__':
    loc = LocationBrancher()
