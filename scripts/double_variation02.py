## imports and setup
import sys
import os
from timeit import default_timer as timer

# sys.stdout = open("./log_simulations.txt", 'w')

time_start = timer()

print "Setting folder paths..."
LCIM_folder_path = "../LCIM_files/"
output_path = "../outputs/final_runs1/"
file_id = "00_uniform"

print "Importing packages..."
execfile("../systems/header01.py")
execfile("../systems/Model_Framework.py")

mfwk = ModelFramework(network_name = "network1", system_file = "../systems/system02.py")


## simulation setup
print "Setting up simulation..."
mfwk.set_time_threshold(200)
mfwk.set_insertion_rate(12, 0)
mfwk.set_insertion_rate(12, 1)

std_nruns = 5000

var_tf_r0 = ("ir", (60, 200), 14, std_nruns, 1, 0)
var_tf_r1 = ("ir", (12, 152), 14, std_nruns, 1, 1)

# more variation tuples go here...

vardat_list = [var_tf_r0, var_tf_r1]
var_codes = [vt[0] for vt in vardat_list]

time_setup_sim = timer()

file_already_exists = os.path.exists(output_path+"dataframes/"+var_codes[0]+var_codes[1]+"_"+file_id+"_roads.csv")
if file_already_exists:
	print "Files for these variables with identifier", file_id, "already exist. Please change the identifier tag."
	sys.exit()

## simulation
print "Running simulation..."
road_df, overall_df = mfwk.DUOVAR(vardat_list, progress_notifications = 30.)

time_sim_out = timer()

## output
try:
	os.makedirs(output_path+"dataframes")
except OSError:
	if not os.path.isdir(output_path+"dataframes"):
		raise

print "Saving dataframes to csv..."
road_df.to_csv(output_path+"dataframes/"+var_codes[0]+var_codes[1]+"_"+file_id+"_roads.csv", sep = "\t")
overall_df.to_csv(output_path+"dataframes/"+var_codes[0]+var_codes[1]+"_"+file_id+"_overall.csv", sep = "\t")

# print "Creating pivoted heatmap dataframe..."
# heatmap_df = road_df[road_df["r_index"] == 1][[var_codes[0]+"_0", var_codes[1]+"_1", "lowest_inst_v"]]
# heatmap_df.to_csv(output_path+"dataframes/"+var_codes[0]+var_codes[1]+"_"+file_id+"_heatmap.csv", sep = "\t")
# hm_df = heatmap_df.pivot(var_codes[0]+"_0", var_codes[1]+"_1", "lowest_inst_v")

# print "Creating heatmap graph, saving..."
# fig_hm = plt.figure()
# ax_hm = fig_hm.add_subplot(111)
# sns.heatmap(hm_df, ax = ax_hm)
# # ax_hm.set_xticklabels(["{:.0f}".format(lt) for lt in hm_df.columns])
# # ax_hm.set_yticklabels(["{:.0f}".format(lt) for lt in hm_df.index])
# plt.xticks([0.5, len(hm_df.columns) - 0.5], ["{:.2f}".format(hm_df.columns[0]), "{:.2f}".format(hm_df.columns[-1])])
# plt.yticks([0.5, len(hm_df.index) - 0.5], ["{:.2f}".format(hm_df.index[-1]), "{:.2f}".format(hm_df.index[0])])
# ax_hm.invert_yaxis()
# plt.savefig(output_path+"graphs/"+var_codes[0]+var_codes[1]+"_"+file_id+".png")

time_end = timer()
print "Simulation succesfully completed."
print "Performance statistics:"
print "\tSetup:\t\t", time_setup_sim - time_start
print "\tSimulation:\t", time_sim_out - time_setup_sim
print "\tOutput:\t\t", time_end - time_sim_out
print "\tTotal:\t\t", time_end - time_start

##
