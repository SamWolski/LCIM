# def csv_save_output(df_list, var_pm, filepath = "./outputs/"):
#     out_list[0].to_csv(filepath+var_pm+"_roads.csv", sep = '\t')
#     out_list[1].to_csv(filepath+var_pm+"_overall.csv", sep = '\t')
#     
# def csv_read_output(var_pm, filepath = "./outputs/"):
#     roads_df = pd.read_csv(filepath+var_pm+"_roads.csv", delim_whitespace = True)
#     overall_df = pd.read_csv(filepath+var_pm+"_overall.csv", delim_whitespace = True)
#     return roads_df, overall_df


default_nsteps = 1000
default_nruns = 1
max_queue = 0

class ModelFramework:
    def __init__(self, network_name, system_file):
        self.system_file = system_file
        self.network_name = network_name
#         self.nw = Network(self.network_name)
        self.time_threshold = 0
        self.reset_network()
        
        # car addition
        self.insertion_rates = np.zeros((len(self.nw.insertion_points)))
        self.insertion_rate_counters = np.zeros((self.insertion_rates.shape))
        
    def set_time_threshold(self, new_tt):
        self.time_threshold = new_tt
    
    def reset_network(self):
        network_name = self.network_name
        exec(open(self.system_file))
        nw.set_time_threshold(self.time_threshold)
        self.nw = nw
        
    def set_insertion_rate(self, rate, road_index):
        self.insertion_rates[road_index] = rate
        self.insertion_rate_counters[road_index] = rate
        
    def check_insertion(self, nn):
		for iinsert, insertion_point in enumerate(self.nw.insertion_points):
			if not(insertion_point.car_insertion_flag):
				self.insertion_rate_counters[iinsert] += 1
			else:
				self.insertion_rate_counters[iinsert] = 0

#         print "counters", self.insertion_rate_counters
		bool_rate = [mm >= rr for mm, rr in zip(self.insertion_rate_counters, self.insertion_rates)]
#         print "bool_rate", bool_rate

#         print "pending cars", [len(ip.pending_cars) for ip in self.nw.insertion_points]
		if any(bool_rate):
			bool_queue = [len(ip.pending_cars) <= max_queue for ip in self.nw.insertion_points]
			return np.where([br and bq for br,bq in zip(bool_rate, bool_queue)])[0]
		else:
			return []
#         return np.where([nn%rr == 0 for rr in self.insertion_rates])[0]
    
    def run_model(self, n_iterations = default_nsteps):
        for nn in xrange(n_iterations):
            insertion_list = self.check_insertion(nn)
#             print "insertion_list", insertion_list
#             print nn, insertion_list
            for ii in insertion_list:
#                 print "Car queued for insertion point(s)", ii, "at iteration", nn
                self.nw.queue_cars(insertion_point = self.nw.insertion_points[ii])
            self.nw.iterate()
    
    
    
    # methods for parameter variation
    
    def VAR_road_insertion_rate(self, road_index = 0, insertion_rate_range = (20,100), n_divisions = 5, iterations_per_run = default_nsteps, runs_per_parameter = default_nruns):
        insertion_rates = np.linspace(insertion_rate_range[0], insertion_rate_range[1], n_divisions)
        insertion_rates = np.array([int(xx) for xx in insertion_rates])        
        
        road_dict = {}
        overall_dict = {}
        
        road_dict["rate"] = []
        road_dict["r_index"] = []
        road_dict["traffic_density"] = []
# 		road_dict["stationary_time"] = []
        road_dict["average_velocity"] = []
# 		road_dict["lowest_inst_v"] = []
        overall_dict["rate"] = []
# 		overall_dict["intersection_crossing_rate"] = []
        overall_dict["removal_event_rate"] = []
        
#         road_dict = {}
#         road_dict["rate"] = []
#         road_dict["r_index"] = []
#         road_dict["traffic_density"] = []
#         road_dict["stationary_time"] = []
#         road_dict["average_velocity"] = []
#         overall_dict = {}
#         overall_dict["rate"] = []
#         overall_dict["intersection_crossing_rate"] = []
#         intersection_dict = {}
#         intersection_dict["rate"] = []
#         intersection_dict["i_index"] = []
#         intersection_dict["intersection_crossing_rate"] = []
#         removal_dict = {}
#         removal_dict["rate"] = []
#         removal_dict["index"] = []
#         removal_dict["removal_event_rate"] = []
        
#         dict_list = [road_dict, intersection_dict]
        run_counter = 1
        
        for rate in insertion_rates:
#             print "Simulating rate:", rate
            for ii in xrange(runs_per_parameter):
                if (run_counter%np.ceil((n_divisions*runs_per_parameter)/30.) == 0):
                    print "Run "+str(run_counter)+"/"+str(n_divisions*runs_per_parameter)
                run_counter += 1
                
                self.reset_network()
                self.set_insertion_rate(rate, road_index)

                # do iteration and get output here
                self.run_model(n_iterations = iterations_per_run)
                run_out_dict = self.nw.get_small_output()
                
#                 for iinter in xrange(len(self.nw.intersections)):
#                     intersection_dict["rate"].append(rate)
#                     intersection_dict["i_index"].append(iinter)
#                     intersection_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][iinter])

                # roads
                for iroad in xrange(len(self.nw.roads)):
                    road_dict["rate"].append(rate)
                    road_dict["r_index"].append(iroad)
                    road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
#                     road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
                    road_dict["average_velocity"].append(run_out_dict["average_velocity2"][iroad])
                overall_dict["rate"].append(rate)
                overall_dict["removal_event_rate"].append(run_out_dict["removal_event_rate"][0])
		road_df = pd.DataFrame(road_dict)
#         intersection_df = pd.DataFrame(intersection_dict)
		overall_df = pd.DataFrame(overall_dict)
#         var_type = "ir"
        return [road_df, overall_df]
    
    def VAR_road_following_distance(self, road_index = 0, following_distance_range = (0.0, 10.0), n_divisions = 5, iterations_per_run = default_nsteps, runs_per_parameter = default_nruns):
    	following_distances = np.linspace(following_distance_range[0], following_distance_range[1], n_divisions)
    	
    	road_dict = {}
        road_dict["following_dist"] = []
        road_dict["r_index"] = []
        road_dict["traffic_density"] = []
        road_dict["stationary_time"] = []
        road_dict["average_velocity"] = []
        road_dict["lowest_inst_v"] = []
        overall_dict = {}
        overall_dict["following_dist"] = []
        overall_dict["intersection_crossing_rate"] = []
#         intersection_dict = {}
#         intersection_dict["following_dist"] = []
#         intersection_dict["i_index"] = []
#         intersection_dict["intersection_crossing_rate"] = []
        for dist in following_distances:
			print "Simulating following distance:", dist
			for ii in xrange(runs_per_parameter):
				if (ii%np.ceil(runs_per_parameter/10) == 0):
					print "Run"+str(ii)+"/"+str(runs_per_parameter)
					
				self.reset_network()
				# parameter variation
				self.nw.roads[road_index].s0 = dist
					
				self.run_model(n_iterations = iterations_per_run)
				run_out_dict = self.nw.get_small_output()
					
				# roads
				for iroad in xrange(len(self.nw.roads)):
					road_dict["following_dist"].append(dist)
					road_dict["r_index"].append(iroad)
					road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
					road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
					road_dict["average_velocity"].append(run_out_dict["average_velocity"][iroad])
					road_dict["lowest_inst_v"].append(run_out_dict["lowest_instantaneous_velocity"][iroad])

# 				for iinter in xrange(len(self.nw.intersections)):
# 					intersection_dict["following_dist"].append(dist)
# 					intersection_dict["i_index"].append(iinter)
# 					intersection_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][iinter])
				
				overall_dict["following_dist"].append(dist)
				overall_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][0])
                    
#         intersection_df = pd.DataFrame(intersection_dict)
        road_df = pd.DataFrame(road_dict)
        overall_df = pd.DataFrame(overall_dict)
        var_type = "fd"
        return var_type, [road_df, overall_df]
		

    def VAR_road_T_factor(self, road_index = 0, T_factor_range = (1.0, 2.0), n_divisions = 5, iterations_per_run = default_nsteps, runs_per_parameter = default_nruns):
    	T_factors = np.linspace(T_factor_range[0], T_factor_range[1], n_divisions)
    	T_factors = np.array([1.0 if T_factors < 1.0 else T_factors])[0]
    	
    	road_dict = {}
        road_dict["T_factor"] = []
        road_dict["r_index"] = []
        road_dict["traffic_density"] = []
        road_dict["stationary_time"] = []
        road_dict["average_velocity"] = []
#         intersection_dict = {}
#         intersection_dict["T_factor"] = []
#         intersection_dict["i_index"] = []
#         intersection_dict["intersection_crossing_rate"] = []
    	overall_dict = {}
    	overall_dict["T_factor"] = []
    	overall_dict["intersection_crossing_rate"] = []
        for Tfac in T_factors:
        	print "Simulating T-factor:", Tfac
        	for ii in xrange(runs_per_parameter):
				if (ii%np.ceil(runs_per_parameter/10) == 0):
					print "Run"+str(ii)+"/"+str(runs_per_parameter)
					
				self.reset_network()
				# parameter variation
				self.nw.roads[road_index].T_factor = Tfac
					
				self.run_model(n_iterations = iterations_per_run)
				run_out_dict = self.nw.get_small_output()
					
				# roads
				for iroad in xrange(len(self.nw.roads)):
					road_dict["T_factor"].append(Tfac)
					road_dict["r_index"].append(iroad)
					road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
					road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
					road_dict["average_velocity"].append(run_out_dict["average_velocity"][iroad])

# 				for iinter in xrange(len(self.nw.intersections)):
# 					intersection_dict["T_factor"].append(Tfac)
# 					intersection_dict["i_index"].append(iinter)
# 					intersection_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][iinter])
				
				overall_dict["T_factor"].append(Tfac)
				overall_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][0])
                    
        road_df = pd.DataFrame(road_dict)
#         intersection_df = pd.DataFrame(intersection_dict)
    	overall_df = pd.DataFrame(overall_dict)
        var_type = "tf"
        return var_type, [road_df, overall_df]
    	
    def VAR_speed_limiter(self, road_index = 0, speed_limiter_range = (0.4, 1.0), n_divisions = 5, iterations_per_run = default_nsteps, runs_per_parameter = default_nruns):
    	speed_limiters = np.linspace(speed_limiter_range[0], speed_limiter_range[1], n_divisions)
    	speed_limiters = np.array([1.0 if (speed_limiters <= 0.0) or (speed_limiters > 1.0) else speed_limiters])[0]
    	
    	road_dict = {}
        road_dict["speed_limiter"] = []
        road_dict["r_index"] = []
        road_dict["traffic_density"] = []
        road_dict["stationary_time"] = []
        road_dict["average_velocity"] = []
#         intersection_dict = {}
#         intersection_dict["T_factor"] = []
#         intersection_dict["i_index"] = []
#         intersection_dict["intersection_crossing_rate"] = []
    	overall_dict = {}
    	overall_dict["speed_limiter"] = []
    	overall_dict["intersection_crossing_rate"] = []
        for speed_lim in speed_limiters:
        	print "Simulating speed limiter:", speed_lim
        	for ii in xrange(runs_per_parameter):
				if (ii%np.ceil(runs_per_parameter/10) == 0):
					print "Run"+str(ii)+"/"+str(runs_per_parameter)

				self.reset_network()
				# parameter variation
				self.nw.roads[road_index].speed_limiter = speed_lim

				self.run_model(n_iterations = iterations_per_run)
				run_out_dict = self.nw.get_small_output()

				# roads
				for iroad in xrange(len(self.nw.roads)):
					road_dict["speed_limiter"].append(speed_lim)
					road_dict["r_index"].append(iroad)
					road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
					road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
					road_dict["average_velocity"].append(run_out_dict["average_velocity"][iroad])

# 				for iinter in xrange(len(self.nw.intersections)):
# 					intersection_dict["T_factor"].append(Tfac)
# 					intersection_dict["i_index"].append(iinter)
# 					intersection_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][iinter])
				
				overall_dict["speed_limiter"].append(speed_lim)
				overall_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][0])
                    
        road_df = pd.DataFrame(road_dict)
#         intersection_df = pd.DataFrame(intersection_dict)
    	overall_df = pd.DataFrame(overall_dict)
        var_type = "sl"
        return var_type, [road_df, overall_df]	
        
    def change_parameter(self, parm_name, parm_value, r_index = 0):
		if parm_name == "ir":
			self.set_insertion_rate(abs(parm_value), r_index)
		elif parm_name == "fd":
			self.nw.roads[r_index].s0 = abs(parm_value)
		elif parm_name == "tf":
			self.nw.roads[r_index].T_factor = abs(parm_value)
		elif parm_name == "sl":
			self.nw.roads[r_index].speed_limiter = parm_value
		else:
			sys.stderr.write("Fatal error: parameter name not recognized.\n")

    def DUOVAR(self, multivar_list, road_index = 0, progress_notifications = 20.):
		if not(len(multivar_list) == 2):
			sys.stderr.write("Error: DUOVAR only handles two variables at a time.\n")
		## output setup
		road_dict = {}
		overall_dict = {}
		
		road_dict["r_index"] = []
		road_dict["traffic_density"] = []
		road_dict["stationary_time"] = []
		road_dict["average_velocity"] = []
		road_dict["lowest_inst_v"] = []
		overall_dict["intersection_crossing_rate"] = []
		
		
		parm_ranges = []
		parm_names = []
		for parm_data in multivar_list:
			parm_ranges.append(np.linspace(parm_data[1][0], parm_data[1][1], parm_data[2]))
			parm_names.append(parm_data[0])
# 			if parm_data[0] == "ir":
# 				parm_ranges[-1] = np.array([int(xx) for xx in parm_ranges[-1]])
# 			elif parm_data[0] == "tf":
# 				parm_ranges[-1] = np.array([1.0 if parm_ranges[-1] < 1.0 else parm_ranges[-1]])[0]
# 			elif parm_data[0] == "sl":
# 				parm_ranges[-1] = np.array([1.0 if (parm_ranges[-1] <= 0.0) or (parm_ranges[-1] > 1.0) else parm_ranges[-1]])[0]
			
# 			self.change_parameter(parm_data[0], parm_data[1][0])
		r_indices = (multivar_list[0][5], multivar_list[1][5])
		parm_keys = (parm_names[0]+"_"+str(r_indices[0]), parm_names[1]+"_"+str(r_indices[1]))
		for pkey in parm_keys:
			road_dict[pkey] = []
			overall_dict[pkey] = []
		
		total_runs = multivar_list[0][2]*multivar_list[1][2]*multivar_list[0][4]*multivar_list[1][4]
		run_counter = 1
		
		for xxx in parm_ranges[0]:
			for ii in xrange(multivar_list[0][4]):
				for yyy in parm_ranges[1]:
					for jj in xrange(multivar_list[1][4]):
						
						if run_counter%np.ceil(total_runs/progress_notifications) == 0:
							print "Run "+str(run_counter)+"/"+str(total_runs)
						run_counter += 1
						
						self.reset_network()
						self.change_parameter(parm_names[0], xxx, r_indices[0])
						self.change_parameter(parm_names[1], yyy, r_indices[1])
						
						self.run_model(n_iterations = multivar_list[0][3])
						run_out_dict = self.nw.get_small_output()
						
						for iroad in xrange(len(self.nw.roads)):
							road_dict[parm_keys[0]].append(xxx)
							road_dict[parm_keys[1]].append(yyy)
							road_dict["r_index"].append(iroad)
							road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
							road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
							road_dict["average_velocity"].append(run_out_dict["average_velocity3"][iroad])
							road_dict["lowest_inst_v"].append(run_out_dict["lowest_instantaneous_velocity"][iroad])
						overall_dict[parm_keys[0]].append(xxx)
						overall_dict[parm_keys[1]].append(yyy)
						overall_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][0])
# 		print road_dict
		road_df = pd.DataFrame(road_dict)
		overall_df = pd.DataFrame(overall_dict)
		return road_df, overall_df

		
		
								
    def VAR_leading_car_u(self, road_index = 0, u_range = (1.0, 10.0), n_divisions = 5, iterations_per_run = default_nsteps, runs_per_parameter = default_nruns, insertion_rate = 20):
        u_values = np.linspace(u_range[0], u_range[1], n_divisions)        
        
        road_dict = {}
        overall_dict = {}
        
        road_dict["u"] = []
        road_dict["r_index"] = []
        road_dict["traffic_density"] = []
# 		road_dict["stationary_time"] = []
        road_dict["average_velocity"] = []
# 		road_dict["lowest_inst_v"] = []
        overall_dict["u"] = []
# 		overall_dict["intersection_crossing_rate"] = []
        overall_dict["removal_event_rate"] = []
        
#         road_dict = {}
#         road_dict["rate"] = []
#         road_dict["r_index"] = []
#         road_dict["traffic_density"] = []
#         road_dict["stationary_time"] = []
#         road_dict["average_velocity"] = []
#         overall_dict = {}
#         overall_dict["rate"] = []
#         overall_dict["intersection_crossing_rate"] = []
#         intersection_dict = {}
#         intersection_dict["rate"] = []
#         intersection_dict["i_index"] = []
#         intersection_dict["intersection_crossing_rate"] = []
#         removal_dict = {}
#         removal_dict["rate"] = []
#         removal_dict["index"] = []
#         removal_dict["removal_event_rate"] = []
        
#         dict_list = [road_dict, intersection_dict]
        run_counter = 1
        
        for u in u_values:
#             print "Simulating rate:", rate
            for ii in xrange(runs_per_parameter):
                if (run_counter%np.ceil((n_divisions*runs_per_parameter)/30.) == 0):
                    print "Run "+str(run_counter)+"/"+str(n_divisions*runs_per_parameter)
                run_counter += 1
                
                self.reset_network()
#                 self.set_insertion_rate(rate, road_index)
                self.set_insertion_rate(insertion_rate, 0)
                self.nw.insertion_points[0].leading_car_u = u

                # do iteration and get output here
                self.run_model(n_iterations = iterations_per_run)
                run_out_dict = self.nw.get_small_output()
                
#                 for iinter in xrange(len(self.nw.intersections)):
#                     intersection_dict["rate"].append(rate)
#                     intersection_dict["i_index"].append(iinter)
#                     intersection_dict["intersection_crossing_rate"].append(run_out_dict["intersection_crossing_rate"][iinter])

                # roads
                for iroad in xrange(len(self.nw.roads)):
                    road_dict["u"].append(u)
                    road_dict["r_index"].append(iroad)
                    road_dict["traffic_density"].append(run_out_dict["traffic_density"][iroad])
#                     road_dict["stationary_time"].append(run_out_dict["stationary_time"][iroad])
                    road_dict["average_velocity"].append(run_out_dict["average_velocity2"][iroad])
                overall_dict["u"].append(u)
                overall_dict["removal_event_rate"].append(run_out_dict["removal_event_rate"][0])
		road_df = pd.DataFrame(road_dict)
#         intersection_df = pd.DataFrame(intersection_dict)
		overall_df = pd.DataFrame(overall_dict)
#         var_type = "ir"
        return [road_df, overall_df]
		
		## actual iteration goes here

##