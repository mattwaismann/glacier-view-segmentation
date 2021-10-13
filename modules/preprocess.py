import tensorflow as tf
import numpy as np

def resize_list_of_numpy_arrays(list_of_numpy_arrays,dim):
    resized_arrays = []
    for array in list_of_numpy_arrays:
        array = np.rollaxis(array,0,3)
        resized_array = tf.image.resize(array, dim)
        resized_arrays.append(resized_array.numpy())
    return resized_arrays

def normalize_list_of_numpy_arrays_to_unit_interval(list_of_numpy_arrays):
    normalized_arrays = []
    for array in list_of_numpy_arrays:
        temp_max = array.max()
        temp_min = array.min()
        normalized_array = (array-temp_min)/(temp_max-temp_min)
        if np.isnan(normalized_array).any():
            normalized_arrays.append(array)
        else:
            normalized_arrays.append(normalized_array)
    return normalized_arrays 
    

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