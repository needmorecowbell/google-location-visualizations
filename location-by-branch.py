import pandas as pd
from datetime import datetime as dt
import json, time, pyglet

class LocationBrancher():
    """docstring for LocationBrancher."""

    df_gps= None
    date_range=None

    window= None
    label = None
    locations = []

    fps_display= pyglet.clock.ClockDisplay()

    def __init__(self):
        self.window= pyglet.window.Window(visible=False)

        self.label = pyglet.text.Label('Location Brancher',
                                    font_size=42,
                                    x=self.window.width//2 , y=self.window.height//2,
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



    def _fillLocationStack(self):

        for x in range(0,len(self.df_gps['datetime'].keys() ) ): # for every element in df_gps...
            if(-1 != int(self.df_gps['alt'][x]) ): #if we didn't set the value to -1 (meaning there is no altitude data for that point)

                print("Location: "+str(self.df_gps['lat'][x])+", "+str(self.df_gps['lon'][x]))
                print("Alt: "+str(self.df_gps['alt'][x]))
                print("Time: "+str(str(self.df_gps['datetime'][x])))
                print("")

                alt= self.df_gps['alt'][x]
                lat = self.df_gps['lat'][x]
                lon = self.df_gps['lon'][x]
                timestamp = self.df_gps['datetime'][x]


                self.locations.append({"alt":alt,"lat":lat,"lon":lon,"time:":timestamp}) # stack the dict on to the top



    def _loadPoint(self):
        location = self.locations.pop()
        if location is not None:
            self.label = pyglet.text.Label("Alt: "+str(location['alt'])+"    Lat: "+str(location['lat'])+"    Lon: "+str(location['lon']),
                                        font_size=16,
                                        x= self.window.height//2 , y=self.window.height//2,
                                        anchor_x='center', anchor_y='center')
        else:
            print("No more Points")
            return -1

    def _reloadDisplay(self):
        self.window.clear()
        self.label.draw()
        self.fps_display.draw()


    def on_draw(self):
        self._reloadDisplay()
        self._loadPoint()

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
