import geopandas as gpd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper,Arrow, OpenHead, NormalHead,GeoJSONDataSource, VeeHead,LinearColorMapper, ColorBar
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import widgetbox,column
from bokeh.io import curdoc,output_notebook
from bokeh.palettes import brewer
import json
from bokeh.models.widgets import CheckboxButtonGroup
import csv



def shapefile_to_json(shapefile):
    shapefile_proj = shapefile.to_crs({'init': 'epsg:3857'})
    #Read data to json.

    json_shp = json.loads(shapefile_proj.to_json()) #loads shapefile json to a dictionary
    json_data = json.dumps(json_shp) #dump-s the json to a string
    # file=open('fuck.txt','w')
    # file.write(json_data)
    # file.close()
    # print(json_data)
    
    return(json_data)



# Weislander chaparral
gdf_chap = gpd.read_file('SimPoints/SimPoints.shp')
# geosource = gdf_chap.to_crs({'init': 'epsg:3857'})
# geosource = convert_GeoPandas_to_Bokeh_format(geosource)
global geosource_json
geosource_json = shapefile_to_json(gdf_chap)

geosource = GeoJSONDataSource(geojson = geosource_json)


#FIA shrubland
shrub_shape = gpd.read_file("Shrub_Sierra/Shrub_Sierra.shp")
global shrub_geosource_json
shrub_geosource_json = shapefile_to_json(shrub_shape)

shrub_geosource = GeoJSONDataSource(geojson = shrub_geosource_json)

# #Temp Background
temp_shape = gpd.read_file("dMAT_shp/dMAT_shp.shp")
global temp_geosource_json
temp_geosource_json = shapefile_to_json(temp_shape)

temp_geosource = GeoJSONDataSource(geojson = temp_geosource_json)

#for color bar
min_range = min(temp_shape["d_MAT"])
max_range = max(temp_shape["d_MAT"])

#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,height = 500, width = 20,
border_line_color=None,location = (0,0), orientation = 'vertical',title="Δ MAT")

# #Alt Layer
alt_shape = gpd.read_file("Alt_Shape/Alt_Shape.shp")
global alt_geosource_json
alt_geosource_json = shapefile_to_json(alt_shape)

alt_geosource = GeoJSONDataSource(geojson = alt_geosource_json)

#for color bar
min_range = min(alt_shape["CA_Alt"])
max_range = max(alt_shape["CA_Alt"])

#Define a sequential multi-hue color palette.
palette = brewer['Oranges'][8]

#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
color_mapper2 = LinearColorMapper(palette = palette, low = min_range, high = max_range)

#Create color bar. 
color_bar2 = ColorBar(color_mapper=color_mapper2, label_standoff=8,height = 500, width = 20,
border_line_color=None,location = (0,0), orientation = 'vertical',title="Alt (m)")


blank_json = {'type': 'FeatureCollection', 
    'features': [{'id': '0', 
        'type': 'Feature', 
        'properties': {'CA_Alt': 0.0}, 
        'geometry': {'type': 'MultiPolygon', 'coordinates': [[[[]]]]}}]}
blank_json_data = json.dumps(blank_json)

blank_json_dmat = {'type': 'FeatureCollection', 
    'features': [{'id': '0', 
        'type': 'Feature', 
        'properties': {'d_MAT': 0.0}, 
        'geometry': {'type': 'MultiPolygon', 'coordinates': [[[[]]]]}}]}
blank_json_data_dmat = json.dumps(blank_json_dmat)
# blank_geosource = GeoJSONDataSource(geojson = blank_json_data)



old_list = []
def checkboxHandler(new):
    global old_list
    remove_this = old_list
    for x in new:
        if x in remove_this:
            remove_this.remove(x)

    add_this = new
    for x in old_list:
        if x in new:
            new.remove(x)

    if 0 in add_this:
        alt_geosource.geojson = alt_geosource_json
        print("add alt")

    elif 0 in remove_this:
        alt_geosource.geojson = blank_json_data
        print("remove alt")
        
    if 1 in add_this:
        temp_geosource.geojson = temp_geosource_json
    elif 1 in remove_this:
        temp_geosource.geojson = blank_json_data_dmat
        
    if 2 in add_this:
        geosource.geojson = geosource_json
    elif 2 in remove_this:
        geosource.geojson = blank_json_data
        
    if 3 in add_this:
        shrub_geosource.geojson = shrub_geosource_json
    elif 3 in remove_this:
        shrub_geosource.geojson = blank_json_data
        

    old_list = new



p = figure(title = 'Chaparral', 
           plot_height = 600 , plot_width = 800,toolbar_location=None,active_scroll="wheel_zoom")


alt_geosource.geojson = blank_json_data
temp_geosource.geojson = blank_json_data_dmat #because of the color fill, it's important to have the own blank here
geosource.geojson = blank_json_data
shrub_geosource.geojson = blank_json_data

p.patches('xs','ys', source = alt_geosource,
              fill_color = {'field' :'CA_Alt', 'transform' : color_mapper2},legend="Altitude")
# temp_geosource.geojson = str(0)
p.patches('xs','ys', source = temp_geosource,
              fill_color = {'field' :'d_MAT', 'transform' : color_mapper},legend="ΔMAT")
# p.patches('xs','ys', source = geosource,
        #           line_color = 'blue', line_width = 0.25, fill_alpha = 1,legend="1930s Chaparral")
# geosource.geojson = str(0)
p.triangle('x','y',source=geosource,color="blue",size=4,legend="1930s Chaparral")
# shrub_geosource.geojson = str(0)
p.circle('x','y', source = shrub_geosource,
              color = 'black', size=4,legend="1990s Shrubland")



#CheckBox
Check_Box = CheckboxButtonGroup(labels=["Altitude","ΔMAT","1930s Chaparral","1990s Shrubland"], active=[])
Check_Box.on_click(checkboxHandler)
checkboxHandler([])




# p.legend.location = "top_right"
p.legend.click_policy="hide"
p.add_layout(color_bar,'right')
p.add_layout(color_bar2,'right')

layout = column(Check_Box,p)
curdoc().add_root(layout)
