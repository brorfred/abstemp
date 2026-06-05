# abstemp

**Absolute Temperature** — analysis of how warming sea-surface temperatures affect
biological accessibility of cooler ocean regions.

The package quantifies *temperature velocity*: the time (in years) it takes for ocean
currents to carry water from a given region to the nearest region that is currently
≥1 °C warmer.  This is computed for three climate periods using ~11 000 global ocean
regions derived from the ECCO particle-tracking model:

| Period | Dataset |
|--------|---------|
| 1985–1990 | OSTIA reanalysis |
| 2019–2023 | OSTIA NRT product |
| 2095–2100 | EC-Earth3-CC SSP5-8.5 |

---

## Reproducing figures with Docker / Podman (recommended)

The fastest way to reproduce all manuscript figures is to run the pre-built
container.  No local Python environment is needed — only
[Docker](https://docs.docker.com/get-started/get-docker/) or
[Podman](https://podman.io/docs/installation).

### Build

```bash
podman build -t abstemp .
```

Replace `podman` with `docker` if using Docker Engine.  The build downloads
all dependencies via [pixi](https://pixi.sh) and takes ~5–10 min on the first
run; subsequent builds reuse the layer cache.

### Run

Mount the data directory (read-only) and an output directory for the figures:

```bash
podman run --rm \
  -v "$(pwd)/src/abstemp/data:/app/src/abstemp/data" \
  -v "$(pwd)/figs:/app/figs" \
  abstemp
```

All figures are written to `figs/` on the host.  The container uses the
`Agg` matplotlib backend — no display required.

The container runs `docker/run_figures.py`, which calls each figure function
in turn and reports pass/fail per figure.

---

## Installation (local development)

The project uses [pixi](https://pixi.sh) to manage a reproducible conda + PyPI
environment.  If pixi is not installed, run
`curl -fsSL https://pixi.sh/install.sh | sh` on macOS/Linux or
`winget install prefix-dev.pixi` on Windows.

```bash
pixi install        # install all dependencies
pixi run python     # launch Python inside the environment
```

All dependencies — including `projmap` — are installed automatically from
PyPI and conda-forge; no extra repositories need to be cloned.

---

## Use case 1 — Bundled data

Most analysis files are tracked in git.  After cloning, only four large SST
NetCDF files need to be downloaded before all figures can be reproduced.

### Files included in git

| File | Size | Description |
|------|------|-------------|
| `src/abstemp/data/abstemp_reg_degvel.parquet` | Per-region degree-velocity for 1985, 2019, 2095 |
| `src/abstemp/data/all_cmip6_hists_ssp585.csv` | CMIP6 SSP5-8.5 area-weighted SST histograms |
| `src/abstemp/data/all_cmip6_hists_ssp245.csv` | CMIP6 SSP2-4.5 area-weighted SST histograms |
| `src/abstemp/data/all_ostia_hists.csv` | OSTIA area-weighted SST histograms |
| `src/abstemp/data/growth_rates.csv` | Observed phytoplankton growth rates vs temperature |

### Files to download after clone

```python
from abstemp import data 

data.setup()
```
Downloads `mintmat_2001-2009.nc`, `ecearth_maxmonsst_2095-2100.nc`, `ostia_maxmonsst_1985-1990.nc`, `ostia_maxmonsst_2019-2023.nc`, and `Longhurst_Regions_2007.nc`.


### Reproduce all figures

```python
import abstemp.figure_scripts as figs

figs.warmest_month_maps()   # three-panel SST map → figs/warmest_sst_map.pdf
figs.global_histograms()    # SST histogram comparison → figs/sst_hist_1985_2019_2095.pdf
figs.growth_model_plot()    # growth-model curves → figs/growth_models.pdf
figs.checkerboard()         # 2°×2° grid diagnostic → figs/checkerboard.pdf
figs.sst_maps()             # max/min/range SST maps → figs/ostia_sst.pdf
figs.tempvel_maps()        # → figs/regdegvel_maps.pdf
figs.tempvel_histogram()     # → figs/regdegvel_hist.pdf
```


#### Figure–data dependency table

| Figure function | Files required | In git? |
|----------------|---------------|---------|
| `warmest_month_maps()` | `ostia_maxmonsst_1985-1990.nc`, `ostia_maxmonsst_2019-2023.nc`, `ecearth_maxmonsst_2095-2100.nc` | No — download |
| `global_histograms()` | `all_cmip6_hists_ssp585.csv`, `all_cmip6_hists_ssp245.csv`, `all_ostia_hists.csv` | Yes |
| `growth_model_plot()` | none | — |
| `checkerboard()` | none | — |
| `sst_maps()` | `mintmat_2001-2009.nc` | Yes |
| `tempvel_maps()` / `tempvel_histogram()` | `abstemp_reg_degvel.parquet` | Yes |

---

## Use case 2 — Full rebuild from external data

This path regenerates every derived file from raw external sources.

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| CDS API credentials | `~/.cdsapirc` — register at [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu) |
| OSTIA archive access | Via `abstemp.seagrid.ostia` (uses Copernicus Marine) |

### Step-by-step

#### 1. Download CMIP6 SST files (24 models × 2 scenarios)

```python
from abstemp.seagrid import cmip6
cmip6.retrieve_all_files()   # needs ~/.cdsapirc; saves to src/abstemp/data/cmip6/
```

This downloads monthly SST for 2090–2100 for all 24 models listed in
`cmip6.cmip6_sst_models` under both `ssp2_4_5` and `ssp5_8_5`.

#### 2. Download or regenerate OSTIA max-month SST files

Download the pre-computed files from the project server:

```python
from abstemp.data import download
download.maxmonsst_fields()   # ecearth_maxmonsst_2095-2100.nc, ostia_maxmonsst_1985-1990.nc, ostia_maxmonsst_2019-2023.nc
```

To regenerate the OSTIA max-month files directly from the raw archive instead:

```python
from abstemp.warmest_month import save_ostia_files
from abstemp.data import generate_maxmonsst_files

save_ostia_files()          # requires OSTIA access; saves ostia_sst_1985-1990.nc and ostia_sst_2019-2023.nc
generate_maxmonsst_files()  # computes ostia_maxmonsst_1985-1990.nc, ostia_maxmonsst_2019-2023.nc, ecearth_maxmonsst_2095-2100.nc
                            # (also requires ecearth_sst_2095-2100.nc from download.maxmonsst_fields())
```

#### 3. Generate SST histogram CSVs

```python
from abstemp.global_sst_histograms import save_cmip_hists, save_ostia_hists

save_cmip_hists()    # reads CMIP6 files from step 1 → all_cmip6_hists_ssp{585,245}.csv
save_ostia_hists()   # requires OSTIA access → all_ostia_hists.csv
```

#### 4. Generate the degree-velocity parquet

The mintmat file (already tracked in git, or downloaded via
`download.mintmat()`) contains the connectivity matrix and all Longhurst
province assignments needed for this step.

```python
from abstemp.tempvel import generate_regdegvel_df
import abstemp, pathlib

df = generate_regdegvel_df()   # requires ostia_maxmonsst_*.nc (step 2) and CMIP6 (2095) access
datadir = pathlib.Path(abstemp.__file__).parent / "data"
df.to_parquet(datadir / "abstemp_reg_degvel.parquet")
```

`generate_regdegvel_df()` calls `regvel_1985`, `regvel_2019`, and `regvel_2095`
which each run `movedegree()` — the main bottleneck (~11 000 region pairs,
several hours per time period).

#### 5. Reproduce all figures

Same as Use case 1, or run the Docker container.

### Regenerating the mintmat SST statistics (rarely needed)

The tracked `mintmat_2001-2009.nc` already contains per-region SST statistics
and Longhurst province codes.  If you need to regenerate them (e.g. after
updating the OSTIA time range):

```python
from abstemp.reg_calculations import add_maxmon, add_longhurst

add_maxmon()       # requires OSTIA access; overwrites mintmat in-place
add_longhurst()    # requires Longhurst_Regions_2007.nc (see below)
```

`Longhurst_Regions_2007.nc` is not tracked in git; download it first:

```python
from abstemp.data import download
download.longhurst_regions()
```

---

## Package layout

```
src/abstemp/
├── __init__.py              Top-level API (open_mintmat_ds, read_*, open_longhurst)
├── warmest_month.py         Load OSTIA SST; save_ostia_files()
├── global_sst_histograms.py Area-weighted SST histogram computation and saving
├── degvelmap.py             Interactive Plotly map of degree-velocity
├── mapview.py               Interactive Plotly map of SST statistics
│
├── data/                    Bundled datasets + download utilities
│   ├── __init__.py          open_warmest_*, open_ostia_*, open_longhurst, max_min_month, generate_maxmonsst_files, all()
│   └── download.py          mintmat(), maxmonsst_fields(), ostia_sst_fields(), longhurst_regions()
│
├── seagrid/                 Grid download/normalisation
│   ├── ostia.py             OSTIA SST download and access (Copernicus Marine)
│   ├── cmip6.py             CMIP6 SST files from CDS API
│   ├── glorys.py            GLORYS12v1 reanalysis from Mercator THREDDS
│   ├── copernicus.py        Copernicus Marine download interface
│   ├── config.py            Dynaconf-based settings loader
│   ├── gridtools.py         Grid-cell spacing and area calculations
│   └── utils/grids.py       pyresample grid definitions
│
├── reg_calculations/        Aggregate gridded SST onto ~11 000 mintmat regions
│   ├── __init__.py          arr_to_regvec, regvec_to_arr, add_maxmon, add_longhurst
│   ├── sst_ostia.py         OSTIA pixel → region mapping
│   ├── sst_cmip6.py         CMIP6 model → region mapping
│   └── longhurst.py         Longhurst province → region mapping
│
├── tempvel/                 Degree-velocity computation
│   └── __init__.py          generate_regdegvel_df(), movedegree(), regvel_*
│
└── figure_scripts/          Manuscript figure generators
    ├── figpref.py           Matplotlib style presets (manuscript / presentation)
    ├── global_hists.py      SST histogram comparison figure
    ├── growth_models.py     Blackford + Norberg-Eppley growth model figures
    ├── maxmonsst.py         Warmest-month SST maps (three time periods)
    ├── methods.py           Methods diagnostic figures (checkerboard, SST maps)
    └── temp_velocities.py   Temperature-velocity maps and histogram
```

---

## Known issues

See [ISSUES.md](ISSUES.md) for the full list.  Items still open that affect
the use cases above:

- Dead code blocks in `sst_ostia.calc_reg_maxmon()` and `regrid()` (D2, D3)
- Bare IP address in `download.maxmonsst_fields()` (S6 — now in `REPO_IP` constant)
