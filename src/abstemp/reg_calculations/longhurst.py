import numpy as np
import xarray as xr
import pandas as pd
import dask
from tqdm import tqdm
from pyresample import bilinear
from pyresample.bucket import BucketResampler
from sklearn.neighbors import BallTree

import abstemp

def nearest_longhurst(mask=None, return_dist=False):
    """Find the nearest mintmat region for each OSTIA full-resolution pixel.

    Builds a haversine BallTree on the mintmat region centroids (from
    ``data/mintmat_2001-2009.nc``) and queries it with every pixel in the
    monthly OSTIA SST dataset to obtain a region assignment for each pixel.

    Parameters
    ----------
    return_dist : bool, optional
        If True, also return the haversine distances (in radians) to the
        nearest region centroid.  Default is False.

    Returns
    -------
    ij : numpy.ndarray
        1-D array of region indices for each OSTIA pixel (flattened).
    dist : numpy.ndarray
        Haversine distances in radians (only returned when
        ``return_dist=True``).
    """
    lh = abstemp.open_longhurst()
    lons,lats = np.meshgrid(lh.lon,lh.lat)
    mask= lh.regions!=0 if mask is None else mask
    latlon = np.deg2rad(np.array([lats[mask], lons[mask]]).T)
    tree = BallTree(latlon, metric="haversine")

    gl = abstemp.open_mintmat_ds()
    latlon2 = np.deg2rad(np.array([gl.reglat[1:],gl.reglon[1:]]).T)
    dist,ij = tree.query(latlon2)
    if return_dist:
        return dist,ij
    return ij


def lh_to_reg(arr, ij=None):
    """Average OSTIA full-resolution SST values into mintmat regions.

    Maps each OSTIA pixel to the nearest mintmat region centroid and computes
    the mean SST within each region.

    Parameters
    ----------
    arr : numpy.ndarray
        2-D array of shape (3600, 7200) with SST values (°C) on the full
        OSTIA 0.05° grid.
    ij : numpy.ndarray, optional
        Precomputed region indices from :func:`nearest_ostia`.  Computed
        on-the-fly if not provided.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by region number (starting at 0) with a single
        column ``sst`` containing the mean SST (°C) for each region.
        Region 0 is set to NaN.
    """
    if isinstance(arr, xr.DataArray):
        name = arr.name
        arr = arr.data
    else:
        name = "data"

    lh = abstemp.open_longhurst()
    mask= lh.regions!=0
    ij = nearest_longhurst(mask=mask) if ij is None else ij
    vec = np.squeeze(arr[mask][ij].T)
    df = pd.DataFrame({"ij":np.arange(len(vec))+1, name:vec})
    df = pd.concat([pd.DataFrame({"ij":0, name:[np.nan]}),df], axis=0)
    df.set_index("ij", inplace=True)
    return df
    #agg(pd.Series.mode)
