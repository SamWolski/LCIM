# script to aggregate dataframes

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from copy import deepcopy

prefix_list = ['{:02d}'.format(xx) for xx in xrange(1,11)]
# print prefix_list

path_stub = "../outputs/final_runs0/"
file_id_stub = "ustd01"
variable = "intersection_crossing_rate"
var_file = "overall"
var_code = "ir"
heatmap_df_list = []

print "Reading files..."
for prefix in prefix_list:
    full_df = pd.read_csv(path_stub+"dataframes/"+var_code+var_code+"_"+prefix+"_"+file_id_stub+"_"+var_file+".csv", delim_whitespace = True)
    if var_file == "roads":
        heatmap_df = full_df[full_df["r_index"] == 1][[var_code+"_0", var_code+"_1", variable]]
    else:
        heatmap_df = full_df[[var_code+"_0", var_code+"_1", variable]]
    heatmap_df_list.append(heatmap_df)
    
means_df = deepcopy(heatmap_df_list[0])
std_df = deepcopy(means_df)


print "Aggregating values..."
for ii in means_df.index:
    newmean = np.mean([df[variable][ii] for df in heatmap_df_list])
    newstd = np.std([df[variable][ii] for df in heatmap_df_list])
    means_df[variable][ii] = newmean
    std_df[variable][ii] = newstd
        
        
print "Saving to csv..."
means_df.to_csv(path_stub+"dataframes/"+var_code+var_code+"_"+file_id_stub+"_"+variable+"_aggregate_means.csv", sep = "\t")
std_df.to_csv(path_stub+"dataframes/"+var_code+var_code+"_"+file_id_stub+"_"+variable+"_aggregate_std.csv", sep = "\t")


##