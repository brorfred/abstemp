
import pathlib

import xarray as xr
import pandas as pd

from abstemp import warmest_month
from abstemp.tempvel import generate_regdegvel_df
from abstemp.seagrid import cmip6
from . import download

def max_min_month(ds):
    """Compute per-pixel maximum and minimum monthly SST statistics.

    Parameters
    ----------
    ds : xarray.Dataset
        Monthly SST dataset with a ``sst`` variable and ``time`` dimension.
        Must start in January and end in December.

    Returns
    -------
    xarray.Dataset
        Dataset with ``lat``/``lon`` dimensions containing:
        ``maxarr``, ``maxmon``, ``minarr``, ``minmon`` (absolute extremes),
        and ``clim_maxarr``, ``clim_maxmon``, ``clim_minarr``, ``clim_minmon``
        (climatological extremes).
    """
    #ds = cmip6.center_on_gmt(cmip6.open_dataset(MODEL))
    if pd.to_datetime(ds.time[0].item()).month != 1:
        raise ValueError("First month must be January")
    if pd.to_datetime(ds.time[-1].item()).month != 12:
        raise ValueError("Last month must be December")

    #n_years = len(ds.time) // 12
    #sst = ds['sst'].fillna(-999).values
    #sst_yr = sst.reshape(n_years, 12, 3600, 7200)
    #maxarr = sst_yr.max(axis=1)
    #maxmon = sst_yr.argmax(axis=1) + 1
    #minarr = sst_yr.min(axis=1)
    #minmon = sst_yr.argmin(axis=1) + 1

    maxarr = ds['sst'].fillna(-999).max(dim='time')
    maxmon = (ds['sst'].fillna(-999).argmax(dim='time') % 12) + 1
    minarr = ds['sst'].fillna(-999).min(dim='time')
    minmon = (ds['sst'].fillna(-999).argmin(dim='time') % 12) + 1

    clim = ds['sst'].groupby('time.month').mean('time')
    clim_maxmon = clim.idxmax('month')
    clim_minmon = clim.idxmin('month')
    clim_maxarr = clim.max('month')
    clim_minarr = clim.min('month')

    dds = xr.Dataset()
    dds["maxarr"] = maxarr
    dds["maxmon"] = maxmon
    dds["minarr"] = minarr
    dds["minmon"] = minmon
    dds["clim_maxarr"] = clim_maxarr
    dds["clim_maxmon"] = clim_maxmon
    dds["clim_minarr"] = clim_minarr
    dds["clim_minmon"] = clim_minmon

    return dds

def generate_maxmonsst_files() -> None:
    """Compute and save max-month SST statistics for all three climate periods.

    Reads the raw monthly SST files via :func:`open_ostia_1985`,
    :func:`open_ostia_2019`, and :func:`open_cmip6_2095`, applies
    :func:`max_min_month` to each, and writes the results to
    ``ostia_maxmonsst_1985-1990.nc``, ``ostia_maxmonsst_2019-2023.nc``, and
    ``ecearth_maxmonsst_2095-2100.nc`` in the package data directory.

    Requires the raw monthly SST files to be present (see
    :func:`abstemp.data.download.ostia_sst_fields` and
    :func:`abstemp.data.download.maxmonsst_fields`).

    Returns
    -------
    None
    """
    datadir = pathlib.Path(__file__).parent
    ds = open_ostia_1985()
    dds = max_min_month(ds)
    dds.to_netcdf(datadir / "ostia_maxmonsst_1985-1990.nc")
    ds = open_ostia_2019()
    dds = max_min_month(ds)
    dds.to_netcdf(datadir / "ostia_maxmonsst_2019-2023.nc")
    ds = open_cmip6_2095()
    dds = max_min_month(ds)
    dds.to_netcdf(datadir / "ecearth_maxmonsst_2095-2100.nc")

def open_ostia_1985() -> xr.Dataset:
    """Open the raw monthly OSTIA reanalysis SST dataset for 1985–1990.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_sst_1985-1990.nc")

def open_ostia_2019() -> xr.Dataset:
    """Open the raw monthly OSTIA NRT SST dataset for 2019–2023.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_sst_2019-2023.nc")

def open_cmip6_2095(model="ecearth") -> xr.Dataset:
    """Open the raw monthly CMIP6 SST dataset for 2095–2100.

    Parameters
    ----------
    model : str, optional
        Model name prefix used to construct the filename
        ``{model}_sst_2095-2100.nc``.  Default is ``"ecearth"``.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / f"{model}_sst_2095-2100.nc")


def open_warmest_1985() -> xr.Dataset:
    """Open the pre-computed OSTIA max-month SST statistics for 1985–1990.

    Returns
    -------
    xarray.Dataset
        Per-pixel SST statistics on a ``lat``/``lon`` grid; see
        :func:`max_min_month` for variable descriptions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_maxmonsst_1985-1990.nc")

def open_warmest_2019() -> xr.Dataset:
    """Open the pre-computed OSTIA NRT max-month SST statistics for 2019–2023.

    Returns
    -------
    xarray.Dataset
        Per-pixel SST statistics on a ``lat``/``lon`` grid; see
        :func:`max_min_month` for variable descriptions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_maxmonsst_2019-2023.nc")

def open_warmest_2095() -> xr.Dataset:
    """Open the pre-computed EC-Earth3-CC max-month SST statistics for 2095–2100.

    Returns
    -------
    xarray.Dataset
        Per-pixel SST statistics on a ``lat``/``lon`` grid; see
        :func:`max_min_month` for variable descriptions.
    """
    return cmip6.center_on_gmt(xr.open_dataset(pathlib.Path(__file__).parent / "ecearth_maxmonsst_2095-2100.nc"))

def open_longhurst() -> xr.Dataset:
    """Open the Longhurst province dataset bundled with the package.

    Returns
    -------
    xarray.Dataset
        Dataset on a regular lat/lon grid with variables ``basins``,
        ``regions``, and ``biomes``.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "Longhurst_Regions_2007.nc")


def all() -> None:
    """Regenerate all derived data files in the package data directory.

    Requires OSTIA access (via njord) for the 1985 and 2019 SST files and
    the raw ``ecearth_sst_2095-2100.nc`` to be present (see
    :func:`abstemp.data.download.maxmonsst_fields`).

    Returns
    -------
    None
    """
    _datadir = pathlib.Path(__file__).parent
    warmest_month.save_ostia_files()
    generate_maxmonsst_files()

    df = generate_regdegvel_df()
    df.to_parquet(_datadir / "abstemp_reg_degvel.parquet")

def setup() -> None:
    """Download all files required for Use Case 1 (bundled-data workflow).

    Fetches the large SST NetCDF files that are not tracked in git
    (``ecearth_maxmonsst_2095-2100.nc``, ``ostia_maxmonsst_1985-1990.nc``,
    ``ostia_maxmonsst_2019-2023.nc``) and the Longhurst province mask, plus
    the mintmat connectivity file from Zenodo.  All other files (parquet,
    CSVs) are already present in the repository.

    Returns
    -------
    None
    """
    download.maxmonsst_fields()
    download.longhurst_regions()
    download.mintmat()
