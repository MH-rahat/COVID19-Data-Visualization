
# from datetime import date, timedelta

# sdate = date(2020, 3, 7)   # start date

# edate=date.today()


# delta = edate - sdate       # as timedelta
# dates=[ ]
# for i in range(delta.days + 1):
#     dates.append(sdate + timedelta(days=i))


import folium
import json
from folium import plugins
import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
import seaborn as sns


with open('BangladeshJson/bd-districts.json', encoding='utf-8') as f:
  data = json.load(f)

with open('BangladeshJson/bangladesh.geojson') as p:
    bdarea = json.load(p)

myDF = pd.DataFrame()
# for x in dates:
#     myDF[str(x)]=0
myDF['zilla'] = [data['districts'][i]['name'] for i in range(0,64)]
myDF['lat'] = [data['districts'][i]['lat'] for i in range(0,64)]
myDF['long'] = [data['districts'][i]['long'] for i in range(0,64)]

#read table from pdf and store it into a dataframe
import tabula
df = tabula.read_pdf("Case_dist_08_May_upload.pdf")
date='May08'
df=df[0]

#get rid of excess columns
df.drop(labels=['Division','Division.1','%'],axis='columns',inplace = True)
#remove the nan values
df.dropna(axis='index',inplace=True)
#merge dhaka district and dhaka city and name it to Dhaka
df.iloc[0,1] += df.iloc[1,1]
df.drop(index = 1,inplace = True)
df.iloc[0,0] = 'Dhaka'
#df.rename( columns={'Unnamed: 0':'Total'}, inplace=True )

#check the data
df.head()
df.info()
df.describe()

#spell-checker
import enchant

#write the name of all zillas in a text file and prepare the custom dictionary
allZilla = '\n'.join(zillas for zillas in list(myDF['zilla']))
with open("zillaNames_mine.txt", "w") as outfile:
    outfile.write(allZilla)
    
zillaList = enchant.PyPWL("zillaNames_mine.txt")

#create the dictionary of total cases
df.set_index('District/City',inplace = True)
caseDict = df.to_dict(orient = 'dict')
caseDict = caseDict['Total']

#the name of B. Baria is too tough to map to Brahamanbaria
caseDict['Brahamanbaria'] = caseDict['B. Baria']
del caseDict['B. Baria']

#correct the zilla name in the data according to the administrative name
for zilla,cases in caseDict.items():
    if(zillaList.check(zilla)):
        print(zilla,cases)
    else:
        #get suggestions for the input word
        suggestions = zillaList.suggest(zilla)
        if(len(suggestions)==0): #if there is no suggestion found
            print('No suggestion found for {}'.format(zilla))
            continue;
        print('{} has been corrected to {} and has cases {}'.format(zilla,suggestions[0],cases))
        caseDict[suggestions[0]] = caseDict[zilla]
        del caseDict[zilla]
#arrange the total cases according to the serial of administrative zilla list
caseList = []
for zilla in myDF['zilla']:
    if zilla in caseDict:
        caseList.append(caseDict[zilla])
    else:
        caseList.append(0)
        
#add a new column in the dataFrame
myDF[str(date)] = caseList
#plt.plot(caseList)
myDF.to_csv('bdcoronalist.csv', encoding='utf-8', index=False)

#initialize the LA County map
#myDF.rename( columns={'2020-05-08':'May08'}, inplace=True )
bdmap = folium.Map(location=[23.6850,90.3563], tiles='Stamen Terrain', zoom_start=7.25)
for i,row in myDF.iterrows():
    row_data=row.May08
    if row_data>=2000:
        a=.9
        r=18
    elif row_data >=1000 and row_data <2000 :
        a=0.8
        r=14
    elif row_data >=300 and row_data <500 :
        a=0.7
        r=12
    elif row_data >=100 and row_data <300 :
        a=0.6
        r=10
    elif row_data >50 and row_data <100 :
        a=0.5
        r=6
    elif row_data >0 and row_data <50 :
        a=0.3
        r=4
    elif row_data==0 :
        a=0
        r=0.001
    r1=int(row_data)
    folium.CircleMarker((row.lat,row.long), radius=r, weight=1,popup=str(row.zilla)+' '+str(r1), color='red', fill_color='red', fill_opacity=a).add_to(bdmap)

# # #heatmap
# # #add the shape of LA County to the map
#folium.GeoJson(bdarea).add_to(bdmap)

# # #add the heatmap. The core parameters are:
# # #--data: a list of points of the form (latitude, longitud e) indicating locations of Starbucks stores

# # #--radius: how big each circle will be around each Starbucks store

# # #--blur: the degree to which the circles blend together in the heatmap

    
#bdmap.add_child(plugins.HeatMap(data=myDF[['lat', 'long']].values, radius=18,blur=5,popup=str(row.zilla)+' '+str(row_data)))

#save the map as an html
bdmap.save('bdcorona_hitmap.html')
#heatmap end


