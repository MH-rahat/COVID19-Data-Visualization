# -*- coding: utf-8 -*-
"""
Created on Fri May 15 15:35:23 2020

@author: MH Rahat
"""
# ref:https://www.jumpingrivers.com/blog/interactive-maps-python-covid-19-spread/
# data:https://public.tableau.com/profile/masud.parvez7954#!/vizhome/COVID-19_15848570974940/Con-GISChange?publish=yes
# data:http://103.247.238.81/webportal/pages/covid19.php

# Import necessary Libraries
import geopandas as gpd #see this for installing geopandas https://www.youtube.com/watch?v=LNPETGKAe0c
import numpy as np
import pandas as pd
import folium
from folium.plugins import TimeSliderChoropleth
import branca.colormap as cm

def correct_date(date_str):
    list_dates = date_str.split("/")
    day = list_dates[0]
    month = list_dates[1]
    year = list_dates[2]
    
    if len(day) == 1:
        day = "0" + day
    if len(month) == 1:
        month = "0" + month
        
    return "/".join([day, month, year])

# In order to map our data, we need a shapefile. A shapefile is a geospatial vector data format. 
# The shapefile format can spatially describe vector features such as points, lines, and polygons.
# In our case, zillas are represented as polygons
country = gpd.read_file("data for time_mapping/bangladesh.json")

#we dont need all of those columns,here "NAME_2 represent Zilla
country=country[["id","NAME_2","geometry"]]

#This line is to make our data loading and visulization faster
country["geometry"] = country["geometry"].simplify(0.01, preserve_topology = False)

#we need to match the column of our corona data
country = country.rename(columns={'NAME_2': 'Zilla'})

# I’ve stored all my data in a directory called “data”.
#  Using the pandas library, we can read in the data
corona_df=pd.read_csv("data for time_mapping/covid_data_til_15_May.csv")

#Seperated and renamed the columns that we need
# corona_df=corona_df[["district_name","Last Updated","iedcr_conrifmed"]]
# corona_df.rename( columns={'district_name':'Zilla','iedcr_conrifmed':'Cases','Last Updated':'Date'}, inplace=True )


#To make the format of date consistance throughtout the dataframe
corona_df["Date"] = corona_df["Date"].apply(correct_date)

#Some zillas are included in the data despite having zero confirmed cases. So we remove these:
corona_df = corona_df[corona_df.Cases != 0]

# We then sort our data by Zilla and reset the index
sorted_df = corona_df.sort_values(['Zilla', 
                     'Date']).reset_index(drop=True)

#If any of the zilla has two entry on single date,we took the sum of them
sum_df = sorted_df.groupby(['Zilla', 'Date'], as_index=False).sum()

# Now we can join the data and the shapefile together
joined_df = sum_df.merge(country, on='Zilla')

# We are going to plot the log of the number of confirmed cases for each zilla, 
# as there are a couple of zillas, such as Dhaka and Narayanganj, 
# with a lot more cases compared to other zillas
joined_df['log_Confirmed'] = np.log10(joined_df['Cases'])

# We also need to convert the Date to unix time in nanoseconds
joined_df['date_sec'] = pd.to_datetime(joined_df['Date'],format='%d/%m/%Y')
joined_df['date_sec']=[(joined_df['date_sec'][i]).timestamp() for i in range(0,joined_df['date_sec'].shape[0])]
joined_df['date_sec'] = joined_df['date_sec'].astype(int).astype(str)

# We can now select the columns needed for the map and discard the others
joined_df = joined_df[['Zilla','Date', 'date_sec', 'log_Confirmed', 'geometry']]

# Time to map

# we define a colour map in terms of the log of the number of confirmed cases
max_colour = max(joined_df['log_Confirmed'])
min_colour = min(joined_df['log_Confirmed'])
cmap = cm.linear.OrRd_09.scale(min_colour, max_colour)
joined_df['colour'] = joined_df['log_Confirmed'].map(cmap)

# we construct our style dictionary
zilla_list = joined_df['Zilla'].unique().tolist()
zilla_idx = range(len(zilla_list))
style_dict = {}
for i in zilla_idx:
    zilla = zilla_list[i]
    result = joined_df[joined_df['Zilla'] == zilla]
    inner_dict = {}
    for _, r in result.iterrows():
        inner_dict[r['date_sec']] = {'color': r['colour'], 'opacity': 0.8}
    style_dict[str(i)] = inner_dict

#Then we need to make a dataframe containing the features for each country:
zilla_df = joined_df[['geometry']]
zilla_gdf = gpd.GeoDataFrame(zilla_df)
zilla_gdf = zilla_gdf.drop_duplicates().reset_index()


# Finally, we create our map and add a colourba
slider_map = folium.Map(location = (23.6850, 90.3563), zoom_start = 6.5,tiles='cartodbpositron')




_ = TimeSliderChoropleth(
    data=zilla_gdf.to_json(),
    styledict=style_dict,

).add_to(slider_map)

_ = cmap.add_to(slider_map)
cmap.caption = "Log of number of confirmed cases"

slider_map.save(outfile='Time_mapping1.html')





