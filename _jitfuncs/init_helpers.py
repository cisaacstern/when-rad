
import numpy as np
from scipy.ndimage import rotate

from numba import jit

@jit(forceobj=True)
def _rotate2azimuth(azimuth, elev_grid):
    '''
    rotates a grid so that North is re-referenced to be
    facing the solar azimuth. See Dozier page XX fig XX.
    '''
    # logger.debug('Step 1: you\'re in the rotater')

    rotation = rotate(input=elev_grid, angle=(-azimuth),
                    reshape=True, order=0, mode='constant', cval=np.nan)
    return rotation

@jit(nopython=True)
def _slope(g, i, j, k):
    '''
    g is the elevation grid, i and j are row indicies, k is the column index
    '''
    if g[j, k] >= g[i, k]:
        return (g[j, k] - g[i, k])/(j-i)
    else:
        return 0

@jit(nopython=True)
def _calc_horizon_indices(grid, horz_arr, nhorz):
    '''
    the horzPt for a given elevG[i, k] is expressed as an index value of elevG[]
    '''

    #horz_arr = np.zeros(grid.shape, dtype=int)
    #nhorz = horz_arr.shape[0]

    # logger.debug(f'Step 2: you\'re in the indexer, nhorz = {nhorz}')

    for k in range(0, nhorz-1):
                        
        horz_arr[nhorz-1, k] = nhorz - 1 #the first entry is its own horizon

        for i in range(nhorz-2, -1, -1): #loop from next-to-end backward to beginning
            
            j = i + 1
            horzj = horz_arr[j, k]
            i_to_j = _slope(grid, i=i, j=j, k=k)
            i_to_horzj = _slope(grid, i=i, j=horzj, k=k)

            while i_to_j < i_to_horzj:
                j = horzj
                horzj = horz_arr[j, k]
                i_to_j = _slope(grid, i=i, j=j, k=k)
                i_to_horzj = _slope(grid, i=i, j=horzj, k=k)

            if i_to_j > i_to_horzj:
                horz_arr[i, k] = j
            elif i_to_j == 0:
                horz_arr[i, k] = i
            else:
                horz_arr[i, k] = horzj

    return horz_arr

@jit(nopython=True)
def _calc_horizon_slope(grid, horz_arr, scale=0.01):
    '''
    takes a rotated elevation grid and a corresponding horzPt array,
    from self.fwdHorz2D, and calculates the slope from each point on
    the elevation grid to its horizon point in the horzPt array.
    returns the elevation grid and a 'slope to horizon (radians)' array
    '''
    # logger.warning('Step 3: you\'re in the sloper. WHAT IS SCALE?')

    shape = grid.shape
    slope_arr = np.zeros(shape)

    for k in range(0, shape[0]):
        for i in range(0, shape[0]):
            slope_arr[i,k] = (
                np.arctan2(
                    grid[horz_arr[i,k], k] - grid[i,k],
                    ((scale * horz_arr[i,k]) - (scale * i))
                )
            )
    return slope_arr