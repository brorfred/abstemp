
import pathlib

import xarray as xr

from abstemp import warmest_month
from abstemp.seagrid import cmip6
from abstemp.tempvel import generate_regdegvel_df
from . import download


def open_warmest_1985() -> xr.Dataset:
    """Open the pre-computed OSTIA warmest-month SST dataset for 1985–1990.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_sst_1985-1990.nc")

def open_warmest_2019() -> xr.Dataset:
    """Open the pre-computed OSTIA NRT warmest-month SST dataset for 2019–2023.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ostia_sst_2019-2023.nc")

def open_warmest_2095() -> xr.Dataset:
    """Open the pre-computed EC-Earth3-CC warmest-month SST dataset for 2095–2100.

    Returns
    -------
    xarray.Dataset
        Monthly SST fields with ``time``, ``lat``, ``lon`` dimensions.
    """
    return xr.open_dataset(pathlib.Path(__file__).parent / "ecearth_sst_2095-2100.nc")

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

    Requires OSTIA access (via njord) for the 1985 and 2019 SST files.
    The EC-Earth 2095 file must be obtained separately via
    :func:`abstemp.data.download.maxmonsst_fields`.

    Returns
    -------
    None
    """
    _datadir = pathlib.Path(__file__).parent
    warmest_month.save_ostia_files()

    df = generate_regdegvel_df()
    df.to_parquet(_datadir / "abstemp_reg_degvel.parquet")

def setup() -> None:
    """Download all files required for Use Case 1 (bundled-data workflow).

    Fetches the three large SST NetCDF files that are not tracked in git
    (``ecearth_sst_2095-2100.nc``, ``ostia_sst_1985-1990.nc``,
    ``ostia_sst_2019-2023.nc``) and the Longhurst province mask, plus the
    mintmat connectivity file from Zenodo.  All other files (parquet, CSVs)
    are already present in the repository.

    Returns
    -------
    None
    """
    download.maxmonsst_fields()
    download.longhurst_regions()
    download.mintmat()
