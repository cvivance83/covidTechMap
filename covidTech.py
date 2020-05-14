import pandas as pd
import geopandas as gpd
import json
from geopy.geocoders import Nominatim
import utm
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, GeoJSONDataSource, HoverTool
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.palettes import brewer
from bokeh.io import output_notebook

f='CovidTech.xlsx'
data=pd.read_excel(f, header = 0)
countries=sorted(list(set([country.strip() for country in data['Pays']])))
# on clean ce qui n'est pas un pays
countries.remove('Israël')
countries.remove('Taïwan')
countries.remove('Canda')

geolocator = Nominatim(user_agent="my-application")
locations = [geolocator.geocode(c) for c in countries]

latitudes=[location.latitude for location in locations]
longitudes=[location.longitude for location in locations]
latDict=dict(zip(countries, latitudes))
longDict=dict(zip(countries, longitudes))

d=dict(zip(countries, [{'Longitude':'', 'Latitude':''} for c in countries]))
for i in range(len(data)):
    if data['Pays'][i] in countries:
        d[data['Pays'][i]]['Nom de la solution'] = data['Nom de la solution'][i]
        d[data['Pays'][i]]['Fonction'] = data['Fonction'][i]
        d[data['Pays'][i]]['Typologie des acteurs de la solution'] = data['Typologie des acteurs de la solution'][i]
        d[data['Pays'][i]]['Tech Used'] = data['Tech Used'][i]
        d[data['Pays'][i]]['Longitude'] = longDict[data['Pays'][i]]
        d[data['Pays'][i]]['Latitude'] = latDict[data['Pays'][i]]

ndf=pd.DataFrame.from_dict(d).T

ndfna = ndf[ndf['Typologie des acteurs de la solution'].notna()]
ndfpc = ndfna.loc[ndfna['Typologie des acteurs de la solution'].str.contains('Public')]
ndfpv = ndfna.loc[ndfna['Typologie des acteurs de la solution'].str.contains('Privé')]

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
geosource = GeoJSONDataSource(geojson =world.to_json())

#Définir une palette 

#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

# Create figure object.
p = figure(title = "Technologies pour contenir l'épidémie de Covid-19", 
           plot_height = 700 ,
           plot_width = 1100, 
           toolbar_location = 'below',)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
# On trace la carte du monde grace a notre objet geosource
states = p.patches('xs','ys', source = geosource,
                   fill_color = 'white',
                   line_color = 'black', 
                   line_width = 0.25, 
                   fill_alpha = 1)

# on définie un objet bokeh ColumnDataSource avec notre dataframe des pays
#Represente les sources de données qui sera dans les points 
sourcepc = ColumnDataSource(
    data=ndfpc
)

sourcepv = ColumnDataSource(
    data=ndfpv
)

# on positionne les points sur la carte grace aux longitudes et latitudes contenues dans ndf
pointspc = p.circle(x="Longitude", y="Latitude", size=15, fill_color="#F7B7A9", fill_alpha=-8, source=sourcepc)
pointspv = p.circle(x="Longitude", y="Latitude", size=10, fill_color="#A9CFF7", fill_alpha=-8, source=sourcepv)
# on met en hover les infos qu'on veut voir quand on un hover un point
p.add_tools(HoverTool(renderers = [pointspv],
                      tooltips = [
                                ('Country','@index'), 
                                ('Name','@{Nom de la solution}'),
                                ('Function','@Fonction'),
                                ('Tech','@{Tech Used}'), 
                                ('Actors', '@{Typologie des acteurs de la solution}')]))


p.add_tools(HoverTool(renderers = [pointspc],
                      tooltips = [
                                ('Country','@index'), 
                                ('Name','@{Nom de la solution}'),
                                ('Function','@Fonction'),
                                ('Tech','@{Tech Used}'), 
                                ('Actors', '@{Typologie des acteurs de la solution}')]))



