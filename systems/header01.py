## header file for imports etc
## also sets up the global variables

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import itertools
import sys
import os.path

from copy import deepcopy
# from IPython import display

## color palettes
palette0 = sns.color_palette("dark")
palette1 = sns.color_palette("muted")

## overall model parameters
dt = 0.1
delta = 4

## generator seeding
execfile(LCIM_folder_path+"LCIM_classes_GeneratorControl01.py")
RndGen.seed_generator(use_previous = False, custom_seed = None)
print "Seed is", RndGen.get_seed()

## importing class files
execfile(LCIM_folder_path+"parameter_dists01.py")
execfile(LCIM_folder_path+"LCIM_classes_car03.py")
execfile(LCIM_folder_path+"LCIM_classes_road03.py")
execfile(LCIM_folder_path+"LCIM_classes_intersection02.py")
execfile(LCIM_folder_path+"LCIM_classes_insertionpoint02.py")
execfile(LCIM_folder_path+"LCIM_classes_network04.py")