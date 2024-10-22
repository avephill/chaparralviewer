library(rgdal)
library(rgeos)
library(shapefiles)
library(raster)

#Hellow Hope this Works
### This File, in conjunction with QGIS was used to reduce the size of source data for use in 
### the bokeh-heroku interactive map

# load shapefiles that are useful for defining boundaries
sierraMask <- readOGR("Source_Data/SierraMask_Tight/SierraMask.shp")



####
## First we get the 1930s Weislander vegetation map
shp <- readOGR('Source_Data/Wieslander_Statewide_CANAD83/Wieslander_Statewide_CANAD83.shp')
types <- shp@data$WHR1_TYPE
ut <- unique(types)
utc <- as.character(ut[grep("Chaparral",ut)])
csh <- shp[shp@data$WHR1_TYPE %in% utc,]
View(csh@data)
scsh <- csh[,c("VTM_ID","WHR1_TYPE")]
scsh@data$WHR1_TYPE <- rep("Chaparral",length(scsh@data$WHR1_TYPE))
# Write the now isolated Chaparral vegetation type to a shapefile
writeOGR(scsh,"ChapShape",layer="ChapShape",driver="ESRI Shapefile") 

## Now using QGIS I simplified ChapShap to fewer polygons using "Simplify" and "Dissolve" tools
##
##

# Read in QGIS Simplified Shapefile and trim to Sierra Nevada boundary
simp <- readOGR("Source_Data/ChapShape/ChapShape.shp")
simp <- spTransform(simp,crs(sierraMask))
simp_sierra <- simp[sierraMask,]

x <- spsample(simp_sierra,n=10000,type="stratified")
x <- SpatialPointsDataFrame(x, data.frame(ID=1:length(x)))
writeOGR(x,"Layers/1930Weislander_Chap_Points",layer="1930Weislander_Chap_Points",driver="ESRI Shapefile")
####

####
## Produce 1990s FIA Shrub shapefile from FIA plots

ca_plot <- read.csv("Source_Data/CA/CA_PLOT.csv")
ca_cond <- read.csv("Source_Data/CA/CA_COND.csv")

#gets all plots that are marked as shrubland Land Cover Class = 2
ca_shrub <- ca_plot[ ca_plot$CN %in% na.omit(ca_cond[ca_cond$LAND_COVER_CLASS_CD_RET==2,"PLT_CN"]),] 
ca_shrub <- ca_shrub[complete.cases(c(ca_shrub$LON,ca_shrub$LAT)),]
xy <- ca_shrub[,c("LON","LAT")]
spdf <- SpatialPointsDataFrame(coords = xy, data = mydf,
                               proj4string = idcrs)
shrub <- spTransform(shrub,crs(sierraMask))
shrub_sierra <- shrub[sierraMask,]
writeOGR(shrub_sierra,"Layers/1990FIA_Shrub_Points",layer="1990FIA_Shrub_Points",driver="ESRI Shapefile")
####

####
# Estimated Vegetation Type https://landfire.gov/version_comparison.php

metadata <- read.csv("~/OfficePortal/Commons/evt_US/CSV_Data/LF_140EVT_09152016.csv",stringsAsFactors = F)
chap_values <- metadata[grep("Chaparral",metadata$CLASSNAME),"VALUE"]

r_sierra <- raster("~/OfficePortal/Commons/evt_sierra.tif")
raster::plot(r_sierra)

evt_chap <- r_sierra
values(evt_chap)[!(values(evt_chap) %in% chap_values)] <- NA
evt_chap_bin <- evt_chap #has multiple chaparral values
values(evt_chap_bin)[!is.na(values(evt_chap_bin))] <- 1
writeRaster(evt_chap_bin,"evt_chap.tif")

#yay binary raster START HERE
evt_chap_bin <- raster("evt_chap.tif")
evt_pts <- rasterToPoints(evt_chap_bin,spatial=T)
evt_pts <- spTransform(evt_pts,crs(idcrs))
evt_pts_smp <- evt_pts[sample(nrow(evt_pts),10000),]
sp::plot(evt_pts_smp,add=T)
evt_pts_smp_sierra <- evt_pts_smp[sierraMask,]
writeOGR(evt_pts_smp_sierra,"Layers/2014Landfire_Chap",layer="2014Landfire_Chap",driver="ESRI Shapefile")

####



#### Produce Shapefiles from environmental Raster Layers

# Altitude
ca_alt <- raster("Source_Data/CA_Alt.asc")
alt_poly <- rasterToPolygons(ca_alt_rounded,dissolve=T) # convert alt to a polygon
crs(alt_poly) <- idcrs
writeOGR(alt_poly,"Layers/Alt_CA","Alt_CA",driver="ESRI Shapefile")

# ΔMAT
x <- raster("Source_Data/d_MAT.nc")
xd <- raster::aggregate(x,fact=10)
xdca <- crop(xd,extent(ca))
values(xdca) <-  round(values(xdca),1)
xdsh <- rasterToPolygons(xdca,dissolve=T)
writeOGR(xdsh,"Layers/dMAT_CA",layer="dMAT_CA",driver="ESRI Shapefile")

