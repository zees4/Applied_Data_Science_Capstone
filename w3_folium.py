# -*- coding: utf-8 -*-
"""W3_Folium.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kXCIVXIdT4hf6AQjIo0zL7d8MgljfN_i
"""

#W3

!pip3 install folium
!pip3 install wget

import folium
import wget
import pandas as pd

# Import folium MarkerCluster plugin
from folium.plugins import MarkerCluster
# Import folium MousePosition plugin
from folium.plugins import MousePosition
# Import folium DivIcon plugin
from folium.features import DivIcon

# Download and read the `spacex_launch_geo.csv`
spacex_csv_file = wget.download('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv')
spacex_df=pd.read_csv(spacex_csv_file)

# Select relevant sub-columns: `Launch Site`, `Lat(Latitude)`, `Long(Longitude)`, `class`
spacex_df = spacex_df[['Launch Site', 'Lat', 'Long', 'class']]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site', 'Lat', 'Long']]
launch_sites_df

# Start location is NASA Johnson Space Center
nasa_coordinate = [29.559684888503615, -95.0830971930759]
site_map = folium.Map(location=nasa_coordinate, zoom_start=10)

# Create a blue circle at NASA Johnson Space Center's coordinate with a popup label showing its name
circle = folium.Circle(nasa_coordinate, radius=1000, color='#d35400', fill=True).add_child(folium.Popup('NASA Johnson Space Center'))
# Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
marker = folium.map.Marker(
    nasa_coordinate,
    # Create an icon as a text label
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % 'NASA JSC',
        )
    )
site_map.add_child(circle)
site_map.add_child(marker)

#1 Mark all launch sites on map

# Initial the map
site_map = folium.Map(location=nasa_coordinate, zoom_start=5)
# For each launch site, add a Circle object based on its coordinate (Lat, Long) values. In addition, add Launch site name as a popup label
for index, row in launch_sites_df.iterrows():
    coordinate = [row['Lat'], row['Long']]
    folium.Circle(coordinate, radius=1000, color='#000000', fill=True).add_child(folium.Popup(row['Launch Site'])).add_to(site_map)
    folium.map.Marker(coordinate, icon=DivIcon(icon_size=(20,20),icon_anchor=(0,0), html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % row['Launch Site'], )).add_to(site_map)
site_map

#2 marking success/failed launches for each site

spacex_df.tail(10)

marker_cluster = MarkerCluster()

# Apply a function to check the value of `class` column
# If class=1, marker_color value will be green
# If class=0, marker_color value will be red
def assign_marker_color(launch_outcome):
    if launch_outcome == 1:
        return 'green'
    else:
        return 'red'

spacex_df['marker_color'] = spacex_df['class'].apply(assign_marker_color)
spacex_df.tail(10)

# Add marker_cluster to current site_map
site_map.add_child(marker_cluster)

# for each row in spacex_df data frame
# create a Marker object with its coordinate
# and customize the Marker's icon property to indicate if this launch was successed or failed,
# e.g., icon=folium.Icon(color='white', icon_color=row['marker_color']
for index, row in spacex_df.iterrows():
    # TODO: Create and add a Marker cluster to the site map
    # marker = folium.Marker(...)
    coordinate = [row['Lat'], row['Long']]
    folium.map.Marker(coordinate, icon=folium.Icon(color='white',icon_color=row['marker_color'])).add_to(marker_cluster)

site_map

#3 calculate distances between launches site to its proximities

# Add Mouse Position to get the coordinate (Lat, Long) for a mouse over on the map
formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)

site_map.add_child(mouse_position)
site_map

from math import sin, cos, sqrt, atan2, radians

def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# find coordinate of the closet coastline
# e.g.,: Lat: 28.56367  Lon: -80.57163
coastline_lat = 28.56385
coastline_lon = -80.56807
launch_site_lat = 28.5632
launch_site_lon = -80.57683
distance_coastline = calculate_distance(launch_site_lat, launch_site_lon, coastline_lat, coastline_lon)

# Create and add a folium.Marker on your selected closest coastline point on the map
# Display the distance between coastline point and launch site using the icon property
# for example
coordinate = [launch_site_lat, launch_site_lon]
distance = distance_coastline
distance_marker = folium.Marker(
   coordinate,
   icon=DivIcon(
       icon_size=(20,20),
       icon_anchor=(0,0),
       html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance),
       )
   )

coordinates =[[launch_site_lat, launch_site_lon], [coastline_lat, coastline_lon]]
lines=folium.PolyLine(locations=coordinates, weight=2)
site_map.add_child(lines)

# find coordinate of the closet city
# using melbourne with zoom rate simmilar to the example graph

city_lat = 28.10348
city_lon = -80.64658
launch_site_lat = 28.5632
launch_site_lon = -80.57683
distance_city = calculate_distance(launch_site_lat, launch_site_lon, city_lat, city_lon)

coordinate2 = [launch_site_lat, launch_site_lon]
distance2 = distance_city
distance_marker2 = folium.Marker(
   coordinate2,
   icon=DivIcon(
       icon_size=(20,20),
       icon_anchor=(0,0),
       html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance2),
       )
   )

coordinates2 =[[launch_site_lat, launch_site_lon], [city_lat, city_lon]]
lines2=folium.PolyLine(locations=coordinates2, weight=2)
site_map.add_child(lines2)

# find coordinate of the closest railway
# using titan III road with zoom rate simmilar to the example graph

railway_lat = 28.56278
railway_lon = -80.58709
launch_site_lat = 28.5632
launch_site_lon = -80.57683
distance_railway = calculate_distance(launch_site_lat, launch_site_lon, railway_lat, railway_lon)

coordinate3 = [launch_site_lat, launch_site_lon]
distance3 = distance_railway
distance_marker3 = folium.Marker(
   coordinate3,
   icon=DivIcon(
       icon_size=(20,20),
       icon_anchor=(0,0),
       html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance3),
       )
   )

coordinates3 =[[launch_site_lat, launch_site_lon], [railway_lat, railway_lon]]
lines3=folium.PolyLine(locations=coordinates3, weight=2)
site_map.add_child(lines3)

# find coordinate of the closest highway
# using Samuel C. Philips Pkwy with zoom rate simmilar to the example graph

highway_lat = 28.56421
highway_lon = -80.57092
launch_site_lat = 28.5632
launch_site_lon = -80.57683
distance_highway = calculate_distance(launch_site_lat, launch_site_lon, highway_lat, highway_lon)

coordinate4 = [launch_site_lat, launch_site_lon]
distance4 = distance_highway
distance_marker4 = folium.Marker(
   coordinate4,
   icon=DivIcon(
       icon_size=(20,20),
       icon_anchor=(0,0),
       html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance4),
       )
   )

coordinates4 =[[launch_site_lat, launch_site_lon], [highway_lat, highway_lon]]
lines4=folium.PolyLine(locations=coordinates4, weight=2)
site_map.add_child(lines4)