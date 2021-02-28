import logging
import datetime

import numpy as np
from numba import jit

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

@jit(forceobj=True)
def _return_center(dat):
    '''
    Parameters
    ==========
    dat : rasterio dataset

    '''
    corner_lng, corner_lat = dat.transform * (0,0)
    res = (dat.bounds.right - dat.bounds.left) / dat.shape[0]
    half = dat.shape[0] / 2
    offset_deg = res * half

    center_lng, center_lat = (
        corner_lng - offset_deg, corner_lat - offset_deg
    )

    return center_lng, center_lat

@jit(forceobj=True)
def _calc_utc_offset(longitude):
    '''
    Parameters
    ==========
    dat : rasterio dataset

    '''        
    offset = np.abs(longitude) / 15
    offset = np.around(offset, decimals=0)
    if longitude < 0:
        return int(-offset)
    else:
        return int(offset)

@jit(forceobj=True)
def _return_utc(offset, local_dt):
    '''
    Parameters
    ==========
    dat : rasterio dataset

    '''
    ldt = local_dt
    day, hour = ldt.day, ldt.hour
    hour = hour - offset

    if hour < 24:
        day = day
    elif hour >= 24:
        day = day+1
        hour = hour-24
    
    logger.warning('_return_utc needs update for edge cases mos/yrs')

    return datetime.datetime(ldt.year, ldt.month, day, hour, ldt.minute,
                            0, 0, tzinfo=datetime.timezone.utc)
