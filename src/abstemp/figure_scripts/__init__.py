"""Figure-generation entry points for the abstemp manuscript.

Each public function in this module produces and saves one or more
publication-ready figures to the ``figs/`` directory.
"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd

import cmap
import projmap

import abstemp
from abstemp import (
    data,
    warmest_month,
    global_sst_histograms,
    tempvel,
)

from .growth_models import plot as growth_model_plot
from .maxmonsst import warmest_months as warmest_month_maps
from .methods import checkerboard, sst_maps
from .global_hists import main_histograms as global_histograms
from .temp_velocities import tempvel_maps, tempvel_histogram

def generate_figures():

    print("Figure 2")
    warmest_month_maps()
    print("Figure 3")
    global_histograms()
    print("Figure 4")
    growth_model_plot()
    print("Figure 5")
    tempvel_maps()
    print("Figure 6")
    sst_maps()
    print("Figure 7")
    tempvel_histogram()
