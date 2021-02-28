import sys
import time

import numpy as np
import matplotlib.pyplot as plt

from _jitfuncs.geo_helpers import(
    _return_center,
    _calc_utc_offset,
    _return_utc,
)
from _jitfuncs.mask_funcs import go_fast

def loop(elevation, sunposition, cachepath):
    '''
    
    '''
    res = elevation.shape[0]

    azis = sunposition[:,3].astype(float, copy=True)
    alts = sunposition[:,2].astype(float, copy=True)
    azis = [int(np.around(x, decimals=0)) for x in azis]
    alts = [int(np.around(x, decimals=0)) for x in alts]

    print('start_utc is ', sunposition[:,1][0])
    print('ending utc is ', sunposition[:,1][-1])
    print('azimuths are, ', azis)
    print('altitudes are, ', alts)

    for i in range(sunposition.shape[0]):

        azi = 180 - azis[i]

        if i == 0:
            start = time.time()
            shadows = go_fast(azi=azi, alt=alts[i], arr=elevation, res=res)
            end = time.time()
            print("i = %s, Elapsed (with comp.) = %s" % (i, end - start))
        else:
            start = time.time()
            shadows = np.dstack(
                (
                    shadows, 
                    go_fast(azi=azi, alt=alts[i], arr=elevation, res=res)
                )
            )
            end = time.time()
            print("i = %s, Elapsed (after comp.) = %s" % (i, end - start))

    print(shadows.shape)

    np.save(f'{cachepath}/shadows.npy', shadows)

if __name__ == '__main__':
    '''
    Run with, e.g.:
    $ python shadow.py 'cachepath'
    '''
    print("This is the name of the program:", sys.argv[0]) 
    print("Argument List:", str(sys.argv))
    cachepath = sys.argv[1]

    start = time.time()

    elevation = np.load(f'{cachepath}/elevation.npy')
    sunposition = np.load(f'{cachepath}/sunposition.npy', allow_pickle=True)

    loop(elevation=elevation, sunposition=sunposition, cachepath=cachepath)

    end = time.time()
    print('Total elapsed = %s' % (end - start))