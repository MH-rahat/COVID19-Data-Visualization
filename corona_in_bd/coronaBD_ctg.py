import folium
import json
from folium import plugins
import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
import seaborn as sns


# with open('D:/Projects/covid-19/bangladesh-geojson/bd-upazilas.json', encoding='utf-8') as f:
#   data = json.load(f)

# with open('bangladesh.geojson') as p:
#     bdarea = json.load(p)

# temp = pd.DataFrame()
# temp['upozila'] = [data['upazilas'][i]['name'] for i in range(0,492)]
# temp['district id'] = [data['upazilas'][i]['district_id'] for i in range(0,492)]

# myDF=pd.DataFrame()
# myDF['upozila']=temp['upozila'][temp['district id']=='43']
# myDF=myDF.reset_index()
# del myDF['index']
# myDF.to_csv('ctgcoronalist.csv', encoding='utf-8', index=False)
myDF=pd.read_csv('ctgcoronalist.csv')
myDF.dropna(axis='index',inplace=True)
myDF.head()

#initialize the LA County map
#myDF.rename( columns={'2020-05-08':'May08'}, inplace=True )
bdmap = folium.Map(location=[22.351641, 91.812999], tiles='Stamen Terrain', zoom_start=10.5)
for i,row in myDF.iterrows():
    row_data=int(row.May08)
    if row_data>=30:
        a=.9
        r=18
    elif row_data >=25 and row_data <30 :
        a=0.8
        r=14
    elif row_data >=15 and row_data <20 :
        a=0.7
        r=12
    elif row_data >=10 and row_data <15 :
        a=0.6
        r=10
    elif row_data >=5 and row_data <10 :
        a=0.5
        r=6
    elif row_data >=3 and row_data <5 :
        a=0.3
        r=4
    elif row_data >0 and row_data <3 :
        a=0.1
        r=1
    folium.CircleMarker((row.lat,row.long), radius=r, weight=1,popup=str(row.Upozila)+' '+str(row_data), color='red', fill_color='red', fill_opacity=a).add_to(bdmap)

# # #heatmap
# # #add the shape of LA County to the map
#folium.GeoJson(bdarea).add_to(bdmap)

# # #add the heatmap. The core parameters are:
# # #--data: a list of points of the form (latitude, longitud e) indicating locations of Starbucks stores

# # #--radius: how big each circle will be around each Starbucks store

# # #--blur: the degree to which the circles blend together in the heatmap

    
bdmap.add_child(plugins.HeatMap(data=myDF[['lat', 'long']].values, radius=18,blur=5))

#save the map as an html
bdmap.save('ctgcorona_hitmap.html')
#heatmap end


