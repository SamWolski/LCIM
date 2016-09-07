## script to re-draw graphs from dataframes

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# sys.stdout = open("./log_graph_redraw.txt", 'w')

path_stub = "../outputs/final_runs1/"
file_id = "00_uniform"
agg_file_id = "ustd01"
variable = "average_velocity"
var_file = "roads"
flag_agg = False
var_codes = ["ir"]#["fd", "ir", "tf"]
heatmap_df_list = []
zmin_list = []
zmax_list = []

print "Reading files..."
for var_code in var_codes:
	full_df = pd.read_csv(path_stub+"dataframes/"+var_code+var_code+"_"+file_id+"_"+var_file+".csv", delim_whitespace = True)
# 	print full_df
# 	heatmap_df_list.append(pd.read_csv(path_stub+"dataframes/"+var_code+var_code+"_"+file_id+"_roads.csv", delim_whitespace = True))
	if var_file == "roads":
		heatmap_df = full_df[full_df["r_index"] == 1][[var_code+"_0", var_code+"_1", variable]]
	else:
		heatmap_df = full_df[[var_code+"_0", var_code+"_1", variable]]
	heatmap_df_list.append(heatmap_df)
for heatmap_df in heatmap_df_list:
	# 	print heatmap_df
	zmin_list.append(min(heatmap_df[variable]))
	zmax_list.append(max(heatmap_df[variable]))
	
print "Computing heatmap limits..."
zmin = min(zmin_list)
zmax = max(zmax_list)
	
try:
	os.makedirs(path_stub+"graphs2")
except OSError:
	if not os.path.isdir(path_stub+"graphs2"):
		raise
try:
	os.makedirs(path_stub+"graphs2/"+variable)
except OSError:
	if not os.path.isdir(path_stub+"graphs2/"+variable):
		raise



for var_code, heatmap_df in zip(var_codes, heatmap_df_list):
	print "Drawing graph for parameter ("+var_code+") with output variable ("+variable+")..."
	hm_df = heatmap_df.pivot(var_code+"_0", var_code+"_1", variable)
		
	fig_hm = plt.figure()
	ax_hm = fig_hm.add_subplot(111)
	sns.heatmap(hm_df, ax = ax_hm, vmin = zmin, vmax = zmax)
	plt.xticks([0.5, len(hm_df.columns) - 0.5], ["{:.2f}".format(hm_df.columns[0]), "{:.2f}".format(hm_df.columns[-1])])
	plt.yticks([0.5, len(hm_df.index) - 0.5], ["{:.2f}".format(hm_df.index[-1]), "{:.2f}".format(hm_df.index[0])])
	ax_hm.invert_yaxis()
    
	if flag_agg:
		plt.savefig(path_stub+"graphs2/"+variable+"/"+var_code+var_code+"_"+agg_file_id+"_"+var_file+".png")
		print "Graph saved to "+path_stub+"graphs2/"+variable+"/"+var_code+var_code+"_"+agg_file_id+"_"+var_file+".png"
	else:
		plt.savefig(path_stub+"graphs2/"+variable+"/"+var_code+var_code+"_"+file_id+".png")
		print "Graph saved to "+path_stub+"graphs2/"+variable+"/"+var_code+var_code+"_"+file_id+".png"

	
	

# 
# path_stub = "../outputs/hometrial02/"
# var_codes = ("ir", "ir")
# file_stub = var_codes[0]+var_codes[1]+"_test0"
# 
# print "Reading file..."
# 
# heatmap_df = pd.read_csv(path_stub+"dataframes/"+file_stub+"_heatmap.csv", delim_whitespace = True)
# hm_df = heatmap_df.pivot(var_codes[0]+"_0", var_codes[1]+"_1", "lowest_inst_v")
# 
# print "Drawing graph..."
# 
# fig_hm = plt.figure()
# ax_hm = fig_hm.add_subplot(111)
# sns.heatmap(hm_df, ax = ax_hm)
# plt.xticks([0.5, len(hm_df.columns) - 0.5], ["{:.2f}".format(hm_df.columns[0]), "{:.2f}".format(hm_df.columns[-1])])
# plt.yticks([0.5, len(hm_df.index) - 0.5], ["{:.2f}".format(hm_df.index[-1]), "{:.2f}".format(hm_df.index[0])])
# ax_hm.invert_yaxis()
# 
# plt.savefig(path_stub+"newgraphs/"+file_stub+".png")
# 
# print "Graph saved to", path_stub+"newgraphs/"+file_stub+".png"

##