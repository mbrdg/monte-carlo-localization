import numpy as np

def fit_normal(values, weights):
    
    # prepare
    values = np.array(values)
    weights = np.array(weights)
        
    # estimate mean
    weights_sum =  weights.sum()
    mean = (values*weights).sum() / weights_sum
   
    # estimate variance
    errors = (values-mean)**2
    variance = (errors*weights).sum() / weights_sum
        
    return (mean, variance)

