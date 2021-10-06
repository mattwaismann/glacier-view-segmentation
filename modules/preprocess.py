import tensorflow as tf
import numpy as np

def resize_and_clean_images(rasters, dim, masks = None):
    rasters_model = []
    masks_model = []
    for idx, raster in enumerate(rasters):
        if masks:
            mask = np.rollaxis(masks[idx],0,3)
            mask = mask[:,:,[0]]
            mask = tf.image.resize(mask, dim)
            masks_model.append(mask)
        raster = np.rollaxis(raster,0,3)
        temp_min = raster.min()
        raster = np.where(raster == temp_min, 0, raster) #addresses the case where negative infinity is in raster
        raster = raster + raster.min() #make sure min is at least 0
        if raster.max() > 0: raster = (raster-raster.min())/(raster.max()-raster.min()) #make sure max is 1
        raster = tf.image.resize(raster, dim)
        rasters_model.append(raster)
    rasters_model_2 = [tensor.numpy() for tensor in rasters_model]
    X_train = np.stack(rasters_model_2)
    if masks: 
        masks_model_2 = [tensor.numpy() for tensor in masks_model] #turns tensors back into numpy arrays
        y_train = np.stack(masks_model_2)
        return X_train,y_train
               
    return X_train

def subset_on_labels(X_train,y_train, labels, oos_ind):
    X_train_sub = X_train[labels,:,:,:]
    y_train_sub = y_train[labels,:,:,:]
    match_inds = []
    for s in range(len(oos_ind)):
        for idx,b in enumerate(range(len(labels))):
            if oos_ind[s] == labels[b]:
                match_inds.append(idx)
    return X_train_sub,y_train_sub, match_inds

def threshold(predictions, thresh):
    preds = predictions.copy()
    preds[preds>thresh] = 1
    preds[preds<thresh] = 0
    return preds

def clean_ts(time_series, dates, glacier_id):
    '''
    time_series: (4d array (time,dim1,dim2,channel))
    dates: (date array) a 1d array of dates
    model: (keras model)
    glacier_id (string) 
    
    '''


    #search middle of image for a 0, if you find one then there is stripes
    ts = time_series.copy()
    dates_ts = dates.copy()
    no_stripes_ind = []
    for t in range(ts.shape[0]):
        if (ts[t,20:100,20:100,0] == 0.01).any():
            pass
        else:
            no_stripes_ind.append(t)
    
    ts = ts[no_stripes_ind]
    dates_ts = dates_ts[no_stripes_ind]
    
    #pred_ts = model.predict(ts)
    #pred_ts_mask = threshold(pred_ts, 0.5)
    
    #sse = []
    #good_mask_example = mask_dict[glacier_id][:,:,0]
    #good_mask_area = np.sum(good_mask_example)
    #for i in range(pred_ts_mask.shape[0]):
        #other = pred_ts_mask[i,:,:,0]
        #sse.append(np.sum((good_mask_example-other)**2))
    #keep_ind = np.where(np.array(sse) < good_mask_area/1)
    #ts = ts[keep_ind]
    #dates_ts = dates_ts[keep_ind]
    return ts, dates_ts