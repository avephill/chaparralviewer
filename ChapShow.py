import geopandas as gpd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, LogColorMapper, GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import widgetbox,column
from bokeh.io import curdoc,output_notebook
from bokeh.palettes import brewer
import json
from bokeh.models.widgets import CheckboxButtonGroup
import csv


##This function is used to convert the shapefiles into a consistent crs and then to JSON

def shapefile_to_json(shapefile):
    shapefile_proj = shapefile.to_crs({'init': 'epsg:3857'}) # change the crs to mercator
    json_shp = json.loads(shapefile_proj.to_json()) #loads shapefile json to a dictionary
    json_data = json.dumps(json_shp) #dump-s the json dictionary to a string
    return(json_data)



### Read in the shapefiles and convert them to geojson data format for use with Bokeh

# CA outline
ca_shp = gpd.read_file("Layers/CA_Outline/CA.shp")
ca_json = shapefile_to_json(ca_shp)
ca_geosource = GeoJSONDataSource(geojson = ca_json)

# 1930s Weislander chaparral
chap_1930_shp = gpd.read_file("Layers/1930Weislander_Chap_Points/1930Weislander_Chap_Points.shp")
chap_1930_json = shapefile_to_json(chap_1930_shp)
chap_1930_geosource = GeoJSONDataSource(geojson = chap_1930_json)

# #1990s FIA shrub_1990land
# shrub_1990_shape = gpd.read_file("Layers/1990FIA_Shrub_Points/1990FIA_Shrub_Points.shp")
# shrub_1990_json = shapefile_to_json(shrub_1990_shape)
# shrub_1990_geosource = GeoJSONDataSource(geojson = shrub_1990_json)

#LANDFIRE Chaparral
landfire_shape = gpd.read_file("Layers/2014Landfire_Chap/2014Landfire_Chap.shp")
landfire_json = shapefile_to_json(landfire_shape)
landfire_geosource = GeoJSONDataSource(geojson = landfire_json)

# dMAT background layer
dMAT_shp = gpd.read_file("Layers/dMAT_CA/dMAT_CA.shp")
dMAT_json = shapefile_to_json(dMAT_shp)
dMAT_geosource = GeoJSONDataSource(geojson = dMAT_json)

# #Alt Layer
alt_shape = gpd.read_file("Layers/Alt_CA/Alt_CA.shp")
alt_json = shapefile_to_json(alt_shape)
alt_geosource = GeoJSONDataSource(geojson = alt_json)



## Here we make blank, dummy geojson data structures to feed to the map when we turn a particular layer "off"

blank_json = {'type': 'FeatureCollection', 
    'features': [{'id': '0', 
        'type': 'Feature', 
        'properties': {'CA_Alt': 0.0}, 
        'geometry': {'type': 'MultiPolygon', 'coordinates': [[[[]]]]}}]}
blank_json_data = json.dumps(blank_json)

# dMAT needs its own because it has unique property names that is needed for the color_bar
blank_json_dmat = {'type': 'FeatureCollection', 
    'features': [{'id': '0', 
        'type': 'Feature', 
        'properties': {'d_MAT': 0.0}, 
        'geometry': {'type': 'MultiPolygon', 'coordinates': [[[[]]]]}}]}
blank_json_data_dmat = json.dumps(blank_json_dmat)



### The following function handles a checkbox check/uncheck event. 
### When an element is selected, it passes all current selections to this 
### function, compares it to the old list of selected elements, and selectively
### enables/disables layers on the map
checkbox_labels = ["Altitude","ΔMAT","1930s Chaparral","2010s Chaparral"]

old_list = []
def checkbox_handler(new):
    
    new_list = [checkbox_labels[i] for i in new] # This converts the selected element index to the label name
    print(new_list)
    global old_list # Make this variable global so it carries over for next run
    remove_this = old_list # Elements in the list will be removed from map
    for x in new_list: # If elements in the old list are not found in the new list, then keep them in the remove_this variable
        if x in remove_this:
            remove_this.remove(x)

    add_this = new_list # Elements in the list will be added to map
    for x in old_list:
        if x in add_this:
            add_this.remove(x)


    ## If the name of a layer has been found in either remove_this or add_this, do either action by populating
    ## the geojson with data (blank or real)

    if "Altitude" in add_this: 
        alt_geosource.geojson = alt_json
    elif "Altitude" in remove_this:
        alt_geosource.geojson = blank_json_data

    if "ΔMAT" in add_this:
        dMAT_geosource.geojson = dMAT_json
    elif "ΔMAT" in remove_this:
        dMAT_geosource.geojson = blank_json_data_dmat
        
    if "1930s Chaparral" in add_this:
        chap_1930_geosource.geojson = chap_1930_json
    elif "1930s Chaparral" in remove_this:
        chap_1930_geosource.geojson = blank_json_data
        
    # if "1990s Shrubland" in add_this:
    #     shrub_1990_geosource.geojson = shrub_1990_json
    # elif "1990s Shrubland" in remove_this:
    #     shrub_1990_geosource.geojson = blank_json_data

    if "2010s Chaparral" in add_this:
        landfire_geosource.geojson = landfire_json
    elif "2010s Chaparral" in remove_this:
        landfire_geosource.geojson = blank_json_data
        
    old_list = new_list


### Set the layers to blank for the initial map
alt_geosource.geojson = blank_json_data
dMAT_geosource.geojson = blank_json_data_dmat #because of the color fill, it's important to have the own blank here
chap_1930_geosource.geojson = blank_json_data
# shrub_1990_geosource.geojson = blank_json_data
landfire_geosource.geojson = blank_json_data



###Prep Color Bars for the environmental variables

def make_colorbar(shapefile_values,color_value_string,color_bar_title):

    #get the min and max values of shapefile
    min_range = min(shapefile_values) 
    max_range = max(shapefile_values)

    palette = brewer[color_value_string][8] #Define a sequential multi-hue color palette.

    #Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)

    #Create color bar. 
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,height = 500, width = 20,
    border_line_color=None,location = (0,0), orientation = 'vertical',title=color_bar_title)

    return(color_mapper,color_bar)


dMAT_color_mapper, dMAT_color_bar = make_colorbar(shapefile_values = dMAT_shp["d_MAT"], 
                                                    color_value_string ="YlGnBu",
                                                    color_bar_title = "Δ MAT")

alt_color_mapper, alt_color_bar = make_colorbar(shapefile_values = alt_shape["CA_Alt"], 
                                                    color_value_string = "Greens",
                                                    color_bar_title = "Alt (m)")



### Now we plot the layers

p = figure(title = 'Chaparral', 
              plot_height = 600 , plot_width = 800,toolbar_location=None,active_scroll="wheel_zoom")


p.patches('xs','ys', source = alt_geosource,
              fill_color = {'field' :'CA_Alt', 'transform' : alt_color_mapper},legend="Altitude")

p.patches('xs','ys', source = dMAT_geosource,
              fill_color = {'field' :'d_MAT', 'transform' : dMAT_color_mapper},legend="ΔMAT")

p.triangle('x','y',source=chap_1930_geosource,color="orange",size=4,legend="1930s Chaparral")

# p.circle('x','y', source = shrub_1990_geosource,
              # color = 'black', size=4,legend="1990s shrubland")

p.square('x','y', source = landfire_geosource,
              color = 'brown', size=4,legend="Landfire Chaparral")

p.multi_line('xs','ys', source = ca_geosource,color="black")


# Add the CheckBox group
Check_Box = CheckboxButtonGroup(labels=checkbox_labels, active=[])
Check_Box.on_click(checkbox_handler)

# Position the color bars
p.add_layout(alt_color_bar,'right')
p.add_layout(dMAT_color_bar,'right')

layout = column(Check_Box,p)
curdoc().add_root(layout)
