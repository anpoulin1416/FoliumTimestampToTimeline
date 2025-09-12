import folium
from folium.plugins import MeasureControl, MousePosition
from folium.plugins import TimestampedGeoJson
import json
import pandas as pd
import geopandas
import numpy as np
from pyproj import CRS, Transformer
from datetime import datetime

colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00']

times = [
    ["2017-06-01T00:00:00", "2017-06-01T23:59:59"],
    ["2017-06-02T00:00:00", "2017-06-02T23:59:59"],
    ["2017-06-03T00:00:00", "2017-06-03T23:59:59"],
    ["2017-06-04T00:00:00", "2017-06-04T23:59:59"],
    ["2017-06-05T00:00:00", "2017-06-05T23:59:59"],
    ["2017-06-06T00:00:00", "2017-06-06T23:59:59"],
    ["2017-06-07T00:00:00", "2017-06-07T23:59:59"],
    ]

dataFile = './data.csv'

df = pd.read_csv(dataFile, delimiter=',')

crs_UTM18N = CRS.from_epsg(32616)
projectionUTMtoLL = Transformer.from_crs(crs_UTM18N, crs_UTM18N.geodetic_crs)

E = 1600614.59
N = 4596006.10

df['X'] += E
df['Y'] += N

UnProjedCoords = projectionUTMtoLL.transform( df['X'], df['Y'])
df['X'] = UnProjedCoords[1]
df['Y'] = UnProjedCoords[0]
gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df['X'], df['Y']), crs="EPSG:4326")

coords = zip(df['X'], df['Y'])
data = df['Count']
popups = df['Count']

names = [
    'Positron',
    'Positron dark',
    'ESRI topo',
    'ESRI imagery',
    'ESRI street',
    ]
attrs = [
    ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
    ('&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
    ('Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'),
    ('Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'),
    ('Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'),
    ]
tiles = [
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    ]

map = folium.Map(location=(df['Y'][0], df['X'][0]), tiles=None, overlay=False, control_scale=True, zoom_start=16)
for index, tileName in enumerate(names):
    folium.TileLayer(name=tileName, attr=attrs[index], tiles=tiles[index], overlay=False, show=False).add_to(map)
lastTile = list(map._children.items())[-1][0]
map._children[lastTile].show = True

folium.plugins.TimestampedGeoJson(
    {
        "type": "FeatureCollection",
        "features": [
            {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": item[1]
                },
            "properties": {
                "times": item[0],
                "popup": item[2],
                "icon": "circle",
                "iconstyle": {"color": colors[item[3]], "fill": "true", "fillOpacity": 1.0, "radius": 5},
            },
        }
        for item in zip(times, coords, popups, data)
        ]
    },
    period="P1D",
    duration="P0D",
    min_speed=0.3,
    max_speed=3.0,
    transition_time=1000,
    auto_play=False,
).add_to(map)

map.save('TimestampedGeoJson.html')
