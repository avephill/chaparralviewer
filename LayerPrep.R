library(rgdal)
library(rgeos)
library(shapefiles)

### This File, in conjunction with QGIS was used to reduce the size of source data for use in 
### the bokeh-heroku interactive map

# load shapefiles that are useful for defining boundaries
sierraMask <- readOGR("Source_Data/SierraMask/SierraMask.shp")

# First we get the 1930s Weislander vegetation map
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

simp <- readOGR("~/Desktop/OfficePortal/Weislander/Rhole/ChapMap/Simplify/Simplify.shp")
shrub <- readOGR("~/Desktop/OfficePortal/Weislander/Rhole/ChapMap/CA_FIA_SHRUB/CA_FIA_SHRUB.shp")

simp <- spTransform(simp,crs(sierraMask))
simp_sierra <- simp[sierraMask,]

shrub <- spTransform(shrub,crs(sierraMask))
shrub_sierra <- shrub[sierraMask,]

writeOGR(simp_sierra,"Simp_Sierra",layer="Simp_Sierra",driver="ESRI Shapefile")
writeOGR(shrub_sierra,"Shrub_Sierra",layer="Shrub_Sierra",driver="ESRI Shapefile")

alt <- raster("/Users/averyhill/Desktop/OfficePortal/ClimateMismatch/ClimateData/Alt_West.gri")
spTransform(alt,idcrs)
alt <- projectRaster(alt,idcrs)
writeRaster(alt,"West_Alt.asc")
ca_alt <- crop(alt,extent(ca))
writeRaster(ca_alt,"CA_Alt.asc")

ca_alt <- raster('/Users/averyhill/Desktop/OfficePortal/Commons/CA_Alt.asc')
ca_ag <- raster::aggregate(ca_alt,fact=60)
raster::plot(ca_ag)
sex <- extent(sierraMask)

sex@ymax <- 40
sierra_alt <- crop(ca_ag,sex)
sierra_alt_ras <- sierra_alt > 1800
sierra_ag_masked <- mask(sierra_alt_ras,sierraMask)
values(sierra_ag_masked)[values(sierra_ag_masked) == 0] <-  NA
raster::plot(sierra_ag_masked)

salt_sp <- as(sierra_ag_masked,"SpatialPolygonsDataFrame")
sal_sp <- rasterToPolygons(sierra_ag_masked,dissolve=T)
crs(sal_sp) <- idcrs
sp::plot(sal_sp)

writeOGR(sal_sp,"SierraMask",layer="SierraMask",driver="ESRI Shapefile")
raster::plot(sierra_ag_masked)

ca_alt_rounded <- ca_ag
values(ca_alt_rounded) <-  round(values(ca_alt_rounded)/1000,0) *1000
values(sierra_ag_masked)[values(sierra_ag_masked) <1000] <-  NA

alt_poly <- rasterToPolygons(ca_alt_rounded,dissolve=T)
sp::plot(alt_poly)
crs(alt_poly) <- idcrs
writeOGR(alt_poly,"Alt_Shape","Alt_Shape",driver="ESRI Shapefile")

shrub <- readOGR("/Users/averyhill/Desktop/OfficePortal/Weislander/Rhole/ChapMap/Shrub_Sierra/Shrub_Sierra.shp")
simp <- readOGR("/Users/averyhill/Desktop/OfficePortal/Weislander/Rhole/ChapMap/Simp_Sierra/Simp_Sierra.shp") 



simpover <- simp[sal_sp,]
shrubover <- shrub[sal_sp,]
sp::plot(shrubover)

x <- spsample(simpover,n=2000,type="random")
x <- SpatialPointsDataFrame(x, data.frame(ID=1:length(x)))
sp::plot(x)
writeOGR(x,"SimPoints","SimPoints",driver="ESRI Shapefile",overwrite_layer = T)


writeOGR(simpover,"Simp_Sierra",layer="Simp_Sierra",driver="ESRI Shapefile")
writeOGR(shrubover,"Shrub_Sierra",layer="Shrub_Sierra",driver="ESRI Shapefile")

cosh <- readOGR("/Users/averyhill/Desktop/OfficePortal/Weislander/Rhole/Dissolved/Dissolved.shp")
sp::plot(cosh)
cosh.test <- cosh
cosh.test@data$WHR1_TYPE <- rep("Chaparral",length(cosh.test@data$WHR1_TYPE))
writeOGR(cosh.test,"ChapShape_test",layer="ChapShape_test",driver="ESRI Shapefile")

View(csh@data)
chap_sp <- data.frame(sp1 = csh@data$SP1_NAME,sp2 = csh@data$SP2_NAME)
chap_sp.uni <- chap_sp[!duplicated(chap_sp),]
sp.uni <- unique(c(as.character(chap_sp.uni$sp1),as.character(chap_sp.uni$sp2)))

ca_plot <- read.csv("/Users/averyhill/Desktop/OfficePortal/FIA/States/CA/CA_PLOT.csv")
ca_cond <- read.csv("/Users/averyhill/Desktop/OfficePortal/FIA/States/CA/CA_COND.csv")

#gets all plots that are shrubland
ca_shrub <- ca_plot[ ca_plot$CN %in% na.omit(ca_cond[ca_cond$LAND_COVER_CLASS_CD_RET==2,"PLT_CN"]),] #2 is shrubland (chaparral)
ca_shrub <- ca_shrub[complete.cases(c(ca_shrub$LON,ca_shrub$LAT)),]
xy <- ca_shrub[,c("LON","LAT")]
spdf <- SpatialPointsDataFrame(coords = xy, data = mydf,
                               proj4string = idcrs)
sp::plot(ca_shrub$LON,ca_shrub$LAT)

x <- raster("/Users/averyhill/Desktop/OfficePortal/ClimateMismatch/ClimateData/CMIPdif full/d_MAT.nc")
raster::plot(x)
xd <- raster::aggregate(x,fact=10)
raster::plot(xd)
xdca <- crop(xd,extent(ca))
values(xdca) <-  round(values(xdca),1)
xdsh <- rasterToPolygons(xdca,dissolve=T)
sp::plot(xdsh)
writeOGR(xdsh,"dMAT_shp",layer="dMAT_shp",driver="ESRI Shapefile")

sh <- readOGR("/Users/averyhill/Desktop/CalVeg/CalVeg.shp")
sp::plot(sh)
View(sh@data)

sh <- readOGR("/Users/averyhill/Desktop/ca_eco_l4/ca_eco_l4.shp")
View(sh@data)
types <- sh@data$NA_L3NAME
ut <- unique(types)
ut[grep("Chaparral",ut)]
