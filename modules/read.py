import rasterio
from rasterio.mask import mask
import fiona 
import os
import geopandas as gpd
from rasterio.warp import calculate_default_transform, reproject, Resampling
import pandas as pd
import numpy as np
from datetime import date

# reproject raster
def reproject_raster(infp, outfp, dst_crs='EPSG:4326'):
    with rasterio.open(infp) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'nodata': 0
        })

        with rasterio.open(outfp, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                    dst_nodata = 0)

def get_images_and_masks(tifs,file_path,shp_name,poly_path):
    glac_id_match = [tif.split('.')[0] for tif in tifs]
    print(len(glac_id_match)) #remove tif ending
    polys = gpd.read_file(poly_path + '/{}'.format(shp_name))
    print(polys.shape) #obtain shapevalue geopandas DataFrame
    rel_ids = polys.iloc[:,[0]].isin(glac_id_match).iloc[:,0] #subset the glaciers we have
    polys = polys[rel_ids]
    print(polys.shape) #subset the glaciers we have
    rel_ordered_ids = list(polys.sort_values(by='glac_id').index) #obtain indicies of ordered glaciers we have
    
    with fiona.open(poly_path + '/{}'.format(shp_name)) as shapefile:
        geoms = [feature['geometry'] for feature in shapefile]
    geoms = list(np.array(geoms)[rel_ordered_ids])
     #obtain geoms that match the ordering of glaciers we have
    masks = []        # list of all the masks
    rasters = []  # list of all the rasters in original shape
    for i in range(len(tifs)):
        print(i)
        with rasterio.open(file_path + '/{}'.format(tifs[i])) as src:
            masked, _ = mask(src, [geoms[i]], nodata = 0.0)
            masks.append(masked)
            rasters.append(src.read())
    masks = [mask.astype('bool').astype('int') for mask in masks]
    return (glac_id_match,rasters,masks)

def get_images(tifs,file_path):
    glac_id_match = [tif.split('.')[0] for tif in tifs] #remove tif ending
    rasters = []  # list of all the rasters in original shape
    for i in range(len(tifs)):
        with rasterio.open(file_path + '/{}'.format(tifs[i])) as src:
            rasters.append(src.read())
    return (glac_id_match,rasters)

def get_shapevalue_df():
    return gpd.read_file('polygons/joined.shp')

#### time series ####
def ts_get_images(folder_path, folders):
      # list of all the rasters in original shape
    rasters = []
    dates = []
    for folder in folders:
        ts_tifs = next(os.walk(os.path.join(folder_path,folder)))[2]
        rasters_temp = []
        dates_temp = []
        ts_tifs.sort()
        for i in range(len(ts_tifs)):
           	if '(' in ts_tifs[i] or 'US' in ts_tifs[i]:
           		continue
           	with rasterio.open(os.path.join(folder_path,folder,ts_tifs[i])) as src:
           		rasters_temp.append(np.nan_to_num(src.read()))
           		dates_temp.append(ts_tifs[i])
        rasters.append(rasters_temp)
        dates.append(dates_temp)
    clean_dates = []
    for date_it in dates:
        temp_clean_dates = []
        for sub_date in date_it:
            temp_clean_dates.append(date.fromisoformat(sub_date.split(".")[0]))
        clean_dates.append(temp_clean_dates)
    return(clean_dates,rasters)