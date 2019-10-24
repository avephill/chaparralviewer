import geopandas as gpd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper,Arrow, OpenHead, NormalHead,GeoJSONDataSource, VeeHead,LinearColorMapper, ColorBar
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import widgetbox,column
from bokeh.io import curdoc,output_notebook
from bokeh.palettes import brewer
import json
from bokeh.models.widgets import CheckboxButtonGroup



gdf_chap = gpd.read_file('SimPoints/SimPoints.shp')


# # In[ ]:


# types = set(gdf["WHR1_TYPE"]) #get unique element from list
# regex = re.compile(".*(Chaparral).*")
# chap = [m.group(0) for l in types for m in [regex.search(l)] if m]
# gdf_chap = gdf[gdf["WHR1_TYPE"].isin(chap)]


# In[ ]:


def shapefile_to_bokeh(shapefile):
    shapefile_proj = shapefile.to_crs({'init': 'epsg:3857'})
    #Read data to json.
    json_shp = json.loads(shapefile_proj.to_json())
    json_data = json.dumps(json_shp)
    geosource = GeoJSONDataSource(geojson = json_data)
    return(geosource)


# In[ ]:


# Weislander chaparral
geosource = shapefile_to_bokeh(gdf_chap)


# In[ ]:


#california shapefile
# ca_shap = "CA/CA.shp"
# ca_shp = gpd.read_file(ca_shap)
# ca_geosource = shapefile_to_bokeh(ca_shp)


# In[ ]:


#FIA shrubland
shrub_shape = gpd.read_file("Shrub_Sierra/Shrub_Sierra.shp")
shrub_geosource = shapefile_to_bokeh(shrub_shape)


# In[12]:


# #Temp Background
temp_shape = gpd.read_file("dMAT_shp/dMAT_shp.shp")
temp_geosource = shapefile_to_bokeh(temp_shape)

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
alt_geosource = shapefile_to_bokeh(alt_shape)

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



p = figure(title = 'Chaparral', 
           plot_height = 650 , plot_width = 800,toolbar_location=None,active_scroll="wheel_zoom")
p.patches('xs','ys', source = alt_geosource,
          fill_color = {'field' :'CA_Alt', 'transform' : color_mapper2},legend="Altitude")
p.patches('xs','ys', source = temp_geosource,
          fill_color = {'field' :'d_MAT', 'transform' : color_mapper},legend="ΔMAT")
# p.patches('xs','ys', source = geosource,
#           line_color = 'blue', line_width = 0.25, fill_alpha = 1,legend="1930s Chaparral")
p.triangle('x','y',source=geosource,color="blue",size=4,legend="1930s Chaparral")
p.circle('x','y', source = shrub_geosource,
          color = 'black', size=4,legend="1990s Shrubland")


p.legend.location = "top_right"
p.legend.click_policy="hide"
p.add_layout(color_bar,'right')
p.add_layout(color_bar2,'right')

layout = p
curdoc().add_root(layout)
