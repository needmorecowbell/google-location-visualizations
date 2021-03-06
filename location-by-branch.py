import pandas as pd
from datetime import datetime as dt
import json, time, pyglet, sys
import threading


class LocationBrancher():
    """docstring for LocationBrancher."""

    df_gps= None
    date_range=None
    locations = []
    currentTask=0
	
    # GUI Components
    window_size= [1000,800]
    window= None
    label = None
    time_label= None
    fps_display= pyglet.clock.ClockDisplay()


    def __init__(self):
        self.window= pyglet.window.Window( self.window_size[0], self.window_size[1], visible=False, resizable=False)

        self.label = pyglet.text.Label('Location Brancher',
                                    font_size=42,
                                    x=self.window.width//2 , y=self.window.height//2,
                                    anchor_x='center', anchor_y='center')
        self.time_label = pyglet.text.Label("Current Date:  ",
                                    font_size=16,
                                    x= (self.window.height//8) , y=self.window.height//8,
                                    anchor_x='center', anchor_y='center')
        self.on_draw = self.window.event(self.on_draw) #instead of decorator

        print("Loading History....")
        self.__loadHistory()
        print("Converting Data...")
        self.__convertData()



        print("Visualizing...")
        self._fillLocationStack()
        self.window.set_visible()

        pyglet.app.run()

    def _locationWorker(self, lowLim, maxLim):
        for x in range(lowLim, maxLim): # for every element in df_gps...
            if(-1 != int(self.df_gps['alt'][x]) ): #if we didn't set the value to -1 (meaning there is no altitude data for that point)

                #print("Location: "+str(self.df_gps['lat'][x])+", "+str(self.df_gps['lon'][x]))
                #print("Alt: "+str(self.df_gps['alt'][x]))
                #print("Time: "+str(str(self.df_gps['datetime'][x])))
                #print("")

                alt= self.df_gps['alt'][x]
                lat = self.df_gps['lat'][x]
                lon = self.df_gps['lon'][x]
                timestamp = self.df_gps['datetime'][x]
                self.locations.append({"alt":alt,"lat":lat,"lon":lon,"time":timestamp}) # stack the dict on to the top
                self.currentTask+=1
                #percentage= (self.currentTask / len(self.df_gps['datetime'].keys()) ) * 100
                #print("Tasks Complete: "+str(self.currentTask)+'/'+str(len(self.df_gps['datetime'].keys())))


    def _fillLocationStack(self):
        limit= int(len(self.df_gps['datetime'].keys() ) // 1) # number of points to acquire (1/4 total)
        workerNum= 30
        tasksPerWorker = limit // workerNum

        threads = []
        lowIndex= 0
        for i in range(workerNum):
            print("Worker #"+str(i))
            print("lowIndex:"+str(lowIndex)+"\thighIndex:"+str(lowIndex+tasksPerWorker))
            time.sleep(3)
            t = threading.Thread(target=self._locationWorker, args=(lowIndex, lowIndex+tasksPerWorker))
            threads.append(t)
            lowIndex+=tasksPerWorker
            t.start()

    def _loadPoint(self):
        if(len(self.locations)>0):
            location = self.locations.pop()

            self.label = pyglet.text.Label("Alt: "+str(location['alt'])+"    Lat: "+str(location['lat'])+"    Lon: "+str(location['lon']),
                                        font_size=16,
                                        x= self.window.height//2 , y=self.window.height//2,
                                        align='center',
                                        anchor_x='center',anchor_y='center')
            self.time_label = pyglet.text.Label("Date:  "+str(location['time']),
                                        font_size=12,
                                        x= 10 , y=10,
                                        align="left")
        else:
            print("Stack has been exhausted")


    def _reloadDisplay(self):
        self.window.clear()
        self.label.draw()
        self.time_label.draw()
        #self.fps_display.draw()


    def on_draw(self):
        self._reloadDisplay()

        if(len(self.locations) >0):
            self._loadPoint()
            print("Points Left: "+str(len(self.locations)))

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
