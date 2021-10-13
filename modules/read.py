import rasterio
from rasterio.mask import mask
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

def get_rasters(dir_path_rasters, tifs):
    rasters = []
    for tif in tifs:
        with rasterio.open(os.path.join(dir_path_rasters,tif)) as src:
            rasters.append(src.read())
    return rasters
                          
def get_masks(dir_path_rasters, tifs, df_polys):
    geoms = list(df_polys.geometry)
    masks = []
    for idx,tif in enumerate(tifs):
        with rasterio.open(os.path.join(dir_path_rasters,tif)) as src:
            masked, _ = mask(src, [geoms[idx]], nodata = 0.0)
            masks.append(masked)
    masks = [mask[[0],:,:].astype('bool').astype('int') for mask in masks]
    return masks
    
                

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