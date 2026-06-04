# abstemp.data

Bundled datasets and download utilities for the **abstemp** analysis.

## Bundled files

| File | Description |
|------|-------------|
| `mintmat_2001-2009.nc` | Dijkstra minimum-travel-time matrix between ~11 000 ocean regions, with per-region SST statistics (max/min/climatological) and Longhurst classifications. |
| `ostia_sst_1985-1990.nc` | Monthly OSTIA reanalysis SST, 1985–1990 (pre-computed). |
| `ostia_sst_2019-2023.nc` | Monthly OSTIA NRT SST, 2019–2023 (pre-computed). |
| `ecearth_sst_2095-2100.nc` | Monthly EC-Earth3-CC SSP5-8.5 SST, 2095–2100. |
| `Longhurst_Regions_2007.nc` | Longhurst (2007) biogeochemical province boundaries on a 0.5° grid. |
| `abstemp_reg_degvel.parquet` | Per-region degree-velocity table for 1985, 2019, and 2095. |
| `all_cmip6_hists_ssp585.csv` | Area-weighted SST histograms for all CMIP6 models, SSP5-8.5. |
| `all_cmip6_hists_ssp245.csv` | Area-weighted SST histograms for all CMIP6 models, SSP2-4.5. |
| `all_ostia_hists.csv` | Area-weighted OSTIA SST histograms for 1985–1990 and 2019–2023. |
| `growth_rates.csv` | Observed phytoplankton growth rates vs. temperature (literature compilation). |
| `growth_rates_binned_1_deg.csv` | Same data binned at 1 °C resolution. |
| `cmip6/` | Per-model CMIP6 NetCDF files downloaded via `download.retrieve_all_cmip6_files()`. |

## Public API

```python
from abstemp import data

ds85  = data.open_warmest_1985()   # xarray.Dataset, OSTIA 1985–1990
ds19  = data.open_warmest_2019()   # xarray.Dataset, OSTIA NRT 2019–2023
ds95  = data.open_warmest_2095()   # xarray.Dataset, EC-Earth3-CC 2095–2100
lh    = data.open_longhurst()      # xarray.Dataset, Longhurst provinces
```

## Downloading data

```python
from abstemp.data import download

# Download all CMIP6 SST files (requires a CDS API key in ~/.cdsapirc)
download.retrieve_all_cmip6_files()

# Download the mintmat file from Zenodo
download.mintmat()

# Download pre-computed warmest-month SST files from the project server
download.maxmonsst_fields()

# Download Longhurst province mask
download.longhurst_regions()
```

## Regenerating derived files

```python
from abstemp.data import all
all()   # regenerates ostia_sst_*.nc files and abstemp_reg_degvel.parquet
```
