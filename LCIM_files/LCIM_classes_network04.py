#######################################
## network class version 04
## requires car version 02
## requires road version 03
## requires intersection version 02
## compatible with version 01 of all other classes

## changelog:
## 02: adds optional override following distances for roads (can artificially extend following distance on specific roads), via either variation in jam distance s0 or variation in safe time headway T
## 03: adds standardised output for graphs (pos & v for each road, traffic density and average velocity for each road)
## 04: adds differentation between full output for small examples and minimal output data for large systems


class Network:
	def __init__(self, name):
		self.name = name
		
		## network elements
		self.cars = []
		self.removed_cars = []
		self.roads = []
		self.intersections = []
		self.insertion_points = []
		
		## iteration variables
		self.time = 0
		
		## graphing and display
		self.output_dict = {}
		self.small_output_dict = {}
		self.has_output_run = False
		self.time_threshold = 100
		
	def set_time_threshold(self, new_tt):
		self.time_threshold = new_tt
	
	## network element manipulation
	def add_road(self, road_name, road_length, priority = 0, T_factor = 1.0, s0 = 0.0, road_critical_distance = 0.5):
		'''
		Add road to system. Priority defaults to lowest.
		'''
		new_road = Road(road_name, road_length, priority = priority, s0 = s0, T_factor = T_factor, critical_distance = road_critical_distance)
		self.roads.append(new_road)
		
	def add_insertion_point(self, road_index):
		'''
		Add insertion point at the beginning of a road.
		
		Attempting to add an insertion point to a road which begins with an intersection will raise an error.
		'''
		if not(self.roads[road_index].intersections[0] == None):
			print "********************"
			print "Error 5: Cannot add insertion point onto road with intersection at beginning!"
			print "Details: Road Index:", road_index
			return None
		self.roads[road_index].add_insertion_point()
		self.insertion_points.append(self.roads[road_index].insertion_point)
		
	def add_intersection(self, exit_road_index, entry_road_indices):
		'''
		Add an intersection by specifying one exit road and at least one entry road by indices in the network road list.
		'''
		new_intersection = Intersection(self.roads[exit_road_index], [self.roads[ii] for ii in entry_road_indices], self)
		self.intersections.append(new_intersection)
		self.roads[exit_road_index].intersections[0] = new_intersection
		for entry_road_index in entry_road_indices:
			self.roads[entry_road_index].intersections[1] = new_intersection
			
	
	## car manipulation
	def queue_cars(self, n_cars = 1, insertion_point = None):
		'''
		Command the given insertion points to queue cars, and add them when possible.
		'''
		if insertion_point == None:
			try:
				insertion_point = self.insertion_points[0]
			except:
				print "********************"
				print "Error 6: Network does not currently have existing insertion points."
				return
		for nn in xrange(n_cars):
			insertion_point.generate_car()
	
	
	def add_car(self, insertion_point = None):
		'''
		Add a car from queued cars at the given insertion point (defaults to the first).
		'''
		# default insertion point
		if insertion_point == None:
			insertion_point = self.insertion_points[0]
		
		# get new car for manipulation
		new_car = insertion_point.pending_cars.pop(0)
# 		print "Car ID", new_car.ID, "is being added."
# 		keyID = 110
# 		if new_car.ID == keyID:
# 		print "Car", new_car.ID, "is being added at time", self.time
# 		if insertion_point.leading_car:			
# 			print "The insertion point's leading car is", insertion_point.leading_car.ID
# 		else:
# 			print "The insertion point has no leading car."
		new_car.leading_car = insertion_point.leading_car
		if insertion_point.leading_car:
# 			print "Its leading car is", new_car.leading_car.ID

			# simply add the following car
			insertion_point.leading_car.following_car = new_car
		else:
			# have to check if the new car becomes the entry car into the intersection
			if insertion_point.road.intersections[1]:
				inter = insertion_point.road.intersections[1]
				inter.entry_cars[np.where([rr == insertion_point.road for rr in inter.entry_roads])[0][0]] = new_car
				new_car.intersection[1] = inter
		
		insertion_point.car_insertion_flag = True

# 
# 		try:
# 			insertion_point.leading_car.following_car = new_car
# 		except:
# # 			print "No existing leading car; new car is new leading car"
# 			try:
# 				inter = insertion_point.road.intersections[1]
# 				inter.entry_cars[np.where([rr == insertion_point.road for rr in inter.entry_roads])[0]] = new_car
# 			except:
# # 				print "Road does not have intersection."
# 				pass
# 			else:
# # 				print "Road has intersection."
# 				new_car.intersection[1] = inter
# 				pass
		new_car.set_creation_time(self.time)
		# clean up
		insertion_point.leading_car = new_car
		for car in insertion_point.pending_cars:
			car.leading_car = new_car
		self.cars.append(new_car)
		insertion_point.road.cars.append(new_car)
		
	def remove_car(self, car):
		'''
		Remove the specified car from the system; to be called when the car has driven off an exit road.
		'''
		try:
			self.cars.remove(car)
		except:
			print "********************"
			print "Error 4: Car to be removed ( ID", car.ID, ") could not be found."
		else:
# 			print "Car", car.ID, "has been successfully removed."
			if car.following_car:
# 				print "The following car has ID", car.following_car.ID
				car.following_car.leading_car = None
			else:
# 				print "There is no following car."
				pass
# 			try:
# 				car.following_car.leading_car = None
# 			except:
# 				pass
			car.update(self.time)
			car.removal_time = self.time
			car.road.removal_events.append(self.time)
			car.road.cars.remove(car)
# 			if any(car.road.cars):
# 				print "The last car on the road has ID", car.road.cars[0].ID
# 			else:
# 				print "The road has no last car."
			self.removed_cars.append(car)
			if car.intersection[0]:
				car.intersection[0].remove_exit_car()
			for insertion_point in self.insertion_points:
				if insertion_point.leading_car == car:
# 					print "FLAG"
					insertion_point.leading_car = None
# 			try:  
# 				car.intersection[0].remove_exit_car()
# 			except:
# 				pass

	
	## simulation iteration
	def iterate(self, n_steps = 1, verbose = False):
		'''
		Carry out the simulation for (n_steps) computational iterations.
		 - Iterates through the list of cars currently in system, calculating new parameters for those where neither the car itself nor the leading car are in an intersection (these are handled by the intersection algorithm)
		 - Iterates through the list of intersections, and calculates new parameters for all cars in intersections, and their following cars.
		 - Iterates through the insertion points and adds cars where necessary and possible.
		 - Iterates through all the cars (again), this time physically updating the positions and velocities.
		'''
		for nnstep in xrange(n_steps):
					
			## iteration
			self.time += 1
# 			if verbose: print "\nIterating model at network level\nTime (iterations) is now", self.time
			
			for insertion_point in self.insertion_points:
				insertion_point.car_insertion_flag = False
			
# 			if verbose: print "Iterating through car list..."
			## iterating through cars
			for car in self.cars:
				if car.is_in_intersection():
# 					if verbose: print "Car", car.ID, "is in an intersection, skipping..."
					continue
				elif car.leading_car_is_in_intersection():
# 					if verbose: print "Car", car.ID, "has leading car", car.leading_car.ID, ", which is in an intersection, skipping..."
					continue
				else:
# 					if verbose: print "Calculating new velocity for car", car.ID, "..."
					car.calculate_new_velocity()				
# 			if verbose: print "Initial car list iteration completed."
			
# 			if verbose: print "Iterating through intersection list..."
			## iterating through intersections
			for intersection in self.intersections:
				if intersection.exit_car:
					intersection.exit_car.calculate_new_velocity()
# 				try:
# 					intersection.exit_car.calculate_new_velocity()
# 				except:
# 					pass
# 				else:
# # 					if verbose: print "Calculated new velocity for exit car, ID", intersection.exit_car.ID
# 					pass
				# iteration through entry roads (already sorted in priority order)
				flag_first_road = True
# 				if verbose: print "Iterating through entry road cars..."
				for entry_road, entry_car in zip(intersection.entry_roads, intersection.entry_cars):
					if entry_car == None:
# 						if verbose: print "No entry car found for road, skipping..."
						pass
					# highest priority entry road is unique
					elif flag_first_road and intersection.free_flow_entry:
# 						if verbose: print "Highest-priority entry road is unique."
						entry_car.calculate_new_velocity()
						if entry_car.following_car:
							entry_car.following_car.calculate_new_velocity()
# 						try:
# 							entry_car.following_car.calculate_new_velocity()
# 						except:
# # 							if verbose: print "There is no following car."
# 							pass
# 						else:
# # 							if verbose: print "New velocity calculated for the following car,", entry_car.following_car.ID
# 							pass
						if entry_car.check_intersection_point_passing():
# 							if verbose: print "Car", entry_car.ID, "is passing intersection point."
							intersection.do_car_passing(entry_car)
					# road is not (highest & unique priority)
					elif entry_car.can_pull_out_safely():
# 						print "Car", entry_car.ID, "can pull out safely, doing so..."
# 						print "Its following car has ID", entry_car.following_car.ID
						if entry_car.road.insertion_point and not(entry_car.following_car):
							entry_car.road.insertion_point.leading_car = None
						if entry_car.following_car:
							entry_car.following_car.calculate_new_velocity(intersection.phantom_car)
# 						try:
# 							entry_car.following_car.calculate_new_velocity(intersection.phantom_car)
# # 							if verbose: print "Successfully calculated new velocity for following car using phantom intersection car."
# 						except:
# # 							if verbose: print "There was an error calculating the following car's new velocity."
# 							pass
# 						if verbose: print "Calling the do_pull_out method..."
						entry_car.do_pull_out()
					else:
# 						print "Car", entry_car.ID, "cannot pull out safely."
						entry_car.calculate_new_velocity(intersection.phantom_car)
						if entry_car.following_car:
							entry_car.following_car.calculate_new_velocity()
# 						try:
# 							entry_car.following_car.calculate_new_velocity()
# 						except:
# # 							if verbose: print "No following car found."	
# 							pass
# 						else:
# # 							if verbose: print "Following car is car", entry_car.following_car.ID, " new velocity calculated."
# 							pass
					flag_first_road = False
# 			if verbose: print "Intersection list iteration completed."
			
			
# 			if verbose: print "Updating all cars..."
			## car updating
			for car in self.cars:
				if car.check_removal():
# 					if verbose: print "Car", car.ID, "is scheduled to be removed."
# 					print "Car", car.ID, "is scheduled to be removed at time", self.time
					self.remove_car(car)
				else:
# 					if verbose: print "Car", car.ID, "has been updated."
					car.update(self.time)
# 			if verbose: print "Car updating completed."
			
			
			## do calculations for output data
# 			if verbose: print "\nCarrying out output-related calculations..."
			for road in self.roads:
				road.update_traffic_density()
				road.update_average_velocity()
				
				
# 			if verbose: print "Iterating through insertion points..."
			## insertion point iteration
			for insertion_point in self.insertion_points:
				if any(insertion_point.pending_cars):
# 					if verbose: print "There are pending cars."
					if insertion_point.leading_car == None:
# 						if verbose: print "No cars in front, car added."
						insertion_point.pending_cars[0].v[-1] = insertion_point.pending_cars[0].u
						self.add_car(insertion_point)
					else:
# 						if verbose: print "There is a leading car, ID", insertion_point.leading_car.ID
						if insertion_point.is_road_clear():
# 							if verbose: print "Road is now clear."
							if insertion_point.can_add_car():
# 								if verbose: print "Enough space, adding car", insertion_point.pending_cars[0].ID
								self.add_car(insertion_point)
							else:
# 								if verbose: print "Not enough space, cannot add car."
								pass
						else:
# 							if verbose: print "Road is not clear, cannot add car."
							pass
# 			if verbose: print "Insertion point list iteration completed."
	
	
	## display and output methods


	def get_small_output(self, intersection_crossing_rate = True, removal_event_rate = True, average_velocity = True, traffic_density = True, stationary_time = True, lowest_instantaneous_velocity = True, average_velocity2 = True, average_velocity3 = True):
		
		# master time
# 		self.small_output_dict["master_time_array"] = np.arange(self.time)*dt
		self.small_output_dict["total_time"] = self.time*dt
		
		# average car density per road
		if traffic_density:
			traffic_density = []
			for road in self.roads:
				average_density = np.mean(np.array(road.traffic_density))
				traffic_density.append(average_density)
			self.small_output_dict["traffic_density"] = traffic_density
			
		# average velocity - NOT GOOD!!
		if average_velocity:
			average_velocity = []
			for road in self.roads:
				avv = np.mean(np.array(road.average_velocity))
				average_velocity.append(avv)
			self.small_output_dict["average_velocity"] = average_velocity
			
		# lowest instantaneous velocity
		if lowest_instantaneous_velocity:
			lowest_instantaneous_velocity = []
			for road in self.roads:
				if any(road.average_velocity):
					liv = np.min(np.array(road.average_velocity))
					lowest_instantaneous_velocity.append(liv)
				else:
					lowest_instantaneous_velocity.append(0.0)
			self.small_output_dict["lowest_instantaneous_velocity"] = lowest_instantaneous_velocity

		# intersection crossing events
		if intersection_crossing_rate:
			inter_crossing_rate = []
			for intersection in self.intersections:
				if len(intersection.crossing_events) > 1:
					Dt = (intersection.crossing_events[-1] - intersection.crossing_events[0])*dt
					average_rate = (len(intersection.crossing_events) - 1)/Dt
					inter_crossing_rate.append(average_rate)
				else:
					inter_crossing_rate.append(0.0)
			self.small_output_dict["intersection_crossing_rate"] = inter_crossing_rate
		
		# car removal events
		if removal_event_rate:
			removal_rate = []
			for road in self.roads:
				if len(road.removal_events) > 1:
					Dt = (road.removal_events[-1] - road.removal_events[0])*dt
					average_rate = (len(road.removal_events) - 1)/Dt
					removal_rate.append(average_rate)
				else:
					removal_rate.append(0.0)
			self.small_output_dict["removal_event_rate"] = removal_rate
			
		# average stationary time per car
		if stationary_time:
			static_time_by_road = []
			road_car_counters = []
			for ii in xrange(len(self.roads)):
				static_time_by_road.append([])
				road_car_counters.append(0.0)
			
			for car in self.removed_cars+self.cars:
				for iroad, road in enumerate(self.roads):
					find_roadpos = np.where([xx == road for xx in car.pos_road])[0]
					car_velocities = np.array([car.v[ii] for ii in find_roadpos])
					if any(find_roadpos):
						road_car_counters[iroad] += 1
# 					print car_velocities
					static_time = (car_velocities.shape[0] - np.count_nonzero(car_velocities))*dt
					static_time_by_road[iroad].append(static_time)
			
			road_car_counters = np.array(road_car_counters)
			nonzero_bool = road_car_counters != 0
			
			ast = np.zeros_like(road_car_counters)
			ast[nonzero_bool] = np.sum(np.array(static_time_by_road), 1)[nonzero_bool]/road_car_counters[nonzero_bool]

			self.small_output_dict["stationary_time"] = ast

		# average velocity per car
		if average_velocity2:
			avv2 = []
			road_car_counters = []
			for ii in xrange(len(self.roads)):
				avv2.append([])
				road_car_counters.append(0)
				
			for car in self.removed_cars+self.cars:
				for iroad, road in enumerate(self.roads):
					find_roadpos = np.where([xx == road for xx in car.pos_road])[0]
					if any(find_roadpos):
						car_velocities = np.array([car.v[ii] for ii in find_roadpos])
						road_car_counters[iroad] += 1
						average_velocity = np.mean(car_velocities)
# 						if # iroad == 1:
# 							print average_velocity
						avv2[iroad].append(average_velocity)
			
			road_car_counters = np.array(road_car_counters)
			nonzero_bool = road_car_counters != 0
# 			print nonzero_bool
			
			av2 = np.zeros_like(road_car_counters, dtype = "float")
# 			print avv2
# 			print avv2
# 			print np.array([np.mean(xx) for xx in np.array(avv2)[nonzero_bool]])
# 			print np.array([np.mean(xx) for xx in np.array(avv2)[nonzero_bool]])
# 			print road_car_counters
# 			print nonzero_bool
# 			print np.array(avv2)[0]
# 			av2[nonzero_bool] = np.mean(np.array(avv2), 1)[nonzero_bool]/road_car_counters[nonzero_bool]

			av2[nonzero_bool] = np.array([np.mean(xx) for xx in np.array(avv2)])[nonzero_bool]
# 			print av2
			
			self.small_output_dict["average_velocity2"] = av2
		
		# average velocity per car - only counting after 100s
		if average_velocity3:
			avv3 = []
			road_car_counters = []
			for ii in xrange(len(self.roads)):
				avv3.append([])
				road_car_counters.append(0)
				
			for car in self.removed_cars+self.cars:
# 				if car.creation_time < self.time_threshold:
# 					continue
				for iroad, road in enumerate(self.roads):
# 					find_roadpos = np.where([xx == road for xx in car.pos_road])[0]
# 					find_times = np.where([tt >= self.time_threshold for tt in car.time_iterations])[0]
					find_roadpos = [xx == road for xx in car.pos_road]
					find_times = [tt*dt >= self.time_threshold for tt in car.time_iterations]
					find = np.where([xx & yy for (xx, yy) in zip(find_roadpos, find_times)])[0]
# 					print "car ID", car.ID, "road index", iroad
# 					print find_roadpos
# 					print find_times
# 					print find
# 					if find.shape[0]:
# 						print [car.time_iterations[xx] for xx in find]
# 					print car.creation_time
# 					print car.time_iterations[0]
# 					print find
					if find.shape[0]:
						car_velocities = np.array([car.v[ii] for ii in find])
						average_velocity = np.mean(car_velocities)
# 						if # iroad == 1:
# 							print average_velocity
						road_car_counters[iroad] += 1
						avv3[iroad].append(average_velocity)
			
			road_car_counters = np.array(road_car_counters)
			nonzero_bool = road_car_counters != 0
# 			print nonzero_bool
			
			av3 = np.zeros_like(road_car_counters, dtype = "float")
# 			print avv2
# 			print avv2
# 			print np.array([np.mean(xx) for xx in np.array(avv2)[nonzero_bool]])
# 			print np.array([np.mean(xx) for xx in np.array(avv2)[nonzero_bool]])
# 			print road_car_counters
# 			print nonzero_bool
# 			print np.array(avv2)[0]
# 			av2[nonzero_bool] = np.mean(np.array(avv2), 1)[nonzero_bool]/road_car_counters[nonzero_bool]

			av3[nonzero_bool] = np.array([np.mean(xx) for xx in np.array(avv3)])[nonzero_bool]
# 			print av2
			
			self.small_output_dict["average_velocity3"] = av3
		
		# more small outputs go here...
		
		return self.small_output_dict
		

	# return big output dict with all required graphs
	def get_output(self, full_output = True, master_time = False, full_car_data = False, traffic_density = False, average_velocity = False, intersection_crossings = False, removal_events = False):
		'''
		Returns a dict of output datasets:
			- Individual car positions and velocities per road (can be subsequently plotted using the graph_car_data_per_road method)
		'''
		# master time array
		if master_time or full_output:
			self.output_dict["master_time"] = np.array(range(self.time))*dt
		
		# individual car positions, velocities per road
		if full_car_data or full_output:
			car_data_per_road = []
			for ii in xrange(len(self.roads)):
				car_data_per_road.append([])
			
			for car in self.removed_cars+self.cars:
				for iroad, road in enumerate(self.roads):			
					find_roadpos = np.where([xx == road for xx in car.pos_road])[0]
			
					car_positions = np.array([car.pos[ii] for ii in find_roadpos])
					car_velocities = np.array([car.v[ii] for ii in find_roadpos])
					car_times = np.array([car.time_iterations[ii]*dt for ii in find_roadpos])
			
					tup = (car_times, car_positions, car_velocities, car.L, car.ID)
					car_data_per_road[iroad].append(tup)
		
			self.output_dict["car_data_per_road"] = car_data_per_road
		
		# average car density per road
		if traffic_density or full_output:
			traffic_density = []
			for road in self.roads:
				traffic_density.append(np.array(road.traffic_density))
			self.output_dict["traffic_density"] = traffic_density
		
		# average velocity per road
		if average_velocity or full_output:
			average_velocity = []
			for road in self.roads:
				average_velocity.append(np.array(road.average_velocity))
			self.output_dict["average_velocity"] = average_velocity
		
		# intersection crossing events
		if intersection_crossings or full_output:
			crossing_events = []
			for intersection in self.intersections:
				crossing_events.append(np.array(intersection.crossing_events)*dt)
			self.output_dict["intersection_crossing_events"] = crossing_events
		
		# car removal events
		if removal_events or full_output:
			removal_events = []
			for road in self.roads:
				removal_events.append(np.array(road.removal_events)*dt)
			self.output_dict["car_removal_events"] = removal_events
		
		# more output datasets go here...
		
		
		
		self.has_output_run = True
		return self.output_dict
		
	def run_output_conditional(self):
		if not(self.has_output_run):
			print "The get_output method has not yet been run. Running now..."
			self.get_output()
		
		
	# draw specific graphs
	def graph_car_data_per_road(self, road_index = None, position = True, show_car_lengths = True, velocity = True, diff_time_thresh = True):
		'''
		Draw graphs of individual car data per road, with options to specify either position or velocity. Returns two lists of (figure, axes) tuples; first positions, then velocities. 
		Note that the road_index argument must be a list, even if only one index is specified, eg road_index = [0]. 
		Runs get_output if that method has not yet been run.
		'''
		self.run_output_conditional()
		data = self.output_dict["car_data_per_road"]
		
		# graph for all roads if not specified
		if road_index == None:
			road_index = range(len(self.roads))
		out_fig_pos = []
		out_fig_v = []
		for iroad in road_index:
			road = self.roads[iroad]
			if position:
				pos_fig, pos_ax = road.setup_road_graph_pos()
				for car_data in data[iroad]:
					if diff_time_thresh:
						# differentiate car data below the time threshold
						if any(car_data[0]):
# 							print car_data[0]
							thresh_mask = np.where(car_data[0] < self.time_threshold)[0]
# 							print thresh_mask
# 							print thresh_mask
							ntm = np.where(car_data[0] >= self.time_threshold)[0]
# 							print ntm
							pos_ax.plot(car_data[0][thresh_mask], car_data[1][thresh_mask], color = palette0[2])
							pos_ax.plot(car_data[0][ntm], car_data[1][ntm], color = palette0[0])
							if show_car_lengths:
								pos_ax.fill_between(car_data[0][thresh_mask], car_data[1][thresh_mask] - car_data[3], car_data[1][thresh_mask], color = palette1[2])
								pos_ax.fill_between(car_data[0][ntm], car_data[1][ntm] - car_data[3], car_data[1][ntm], color = palette1[0])
					else:
						# do not differentiate cars below the threshold
						pos_ax.plot(car_data[0], car_data[1], color = palette0[0])
						if show_car_lengths:
							pos_ax.fill_between(car_data[0], car_data[1] - car_data[3], car_data[1], color = palette1[0])

				
# 					c_array = np.array([palette0[0] for ii in xrange(car_data[0].shape[0])])
# 					c_ind = np.array([0 for ii in xrange(car_data[0].shape[0])], dtype = 'int')
# # 					c_array = np.zeros((car_data[0].shape[0], 3), dtype = 'int')
# 					if (iroad == 1) and any(car_data[0]):
# 						c_array[car_data[0] < self.time_threshold, :] = palette0[2]
# 						c_ind[car_data[0] < self.time_threshold] = 2
# 					print c_array.shape
# 					print c_array
# 					if (iroad == 1) and any(car_data[0]):
# 						print car_data[0][0]
# 						if (car_data[0][0] < self.time_threshold):
# 							c_ind = 2
# 						else:
# 							c_ind = 0
# 					else:
# 						c_ind = 0
# 					if any(c_ind):
# 						pos_ax.plot(car_data[0], car_data[1], color = palette0[c_ind])					
# 					if car_data[4] in [2]:
# 						pos_ax.plot(car_data[0], car_data[1], color = palette0[2])
# 					elif car_data[4] in [3]:
# 						pos_ax.plot(car_data[0], car_data[1], color = palette0[3])						
# 					else:
# 						pos_ax.plot(car_data[0], car_data[1], color = palette0[0])
# 						if show_car_lengths:
# 							pos_ax.fill_between(car_data[0], car_data[1] - car_data[3], car_data[1], color = palette1[c_ind])
				out_fig_pos.append([pos_fig, pos_ax])
			if velocity:
				v_fig, v_ax = road.setup_road_graph_v()
				for car_data in data[iroad]:
					v_ax.plot(car_data[0], car_data[2], color = palette0[1])
				out_fig_v.append([v_fig, v_ax])
		return out_fig_pos, out_fig_v
				
	def graph_traffic_densities(self, road_index = None):
		'''
		Draw graphs of overall traffic density across the road. Returns a list of (figure, axes) tuples. 
		Note that the road_index argument must be a list, even if only one index is specified, eg road_index = [0]. 
		Runs get_output if that method has not yet been run.
		'''
		self.run_output_conditional()
		data = self.output_dict["traffic_density"]
		road_names = []
		
		fig = plt.figure()
		ax = fig.add_subplot(1,1,1)
		
		if road_index == None:
			road_index = range(len(self.roads))

		for ii in road_index:
			ax.plot(self.output_dict["master_time"], data[ii])
			road_names.append(self.roads[ii].name)

		ax.set_xlabel("time")
		ax.set_ylabel("traffic density (cars/m)")
		ax.legend(road_names)
		
		return fig, ax
		
	def graph_average_velocities(self, road_index = None):
		'''
		Draw graphs of average traffic velocity across the entire road. Returns a list of (figure, axes) tuples. 
		Note that the road_index argument must be a list, even if only one index is specified, eg road_index = [0]. 
		Runs get_output if that method has not yet been run.
		'''
		self.run_output_conditional()
		data = self.output_dict["average_velocity"]
		road_names = []
		
		fig = plt.figure()
		ax = fig.add_subplot(1,1,1)
		
		if road_index == None:
			road_index = range(len(self.roads))

		for ii in road_index:
			ax.plot(self.output_dict["master_time"], data[ii])
			road_names.append(self.roads[ii].name)
			
		ax.set_xlim([0, self.output_dict["master_time"][-1]])
		ax.set_xlabel("time")
		ax.set_ylabel("average velocity (m/s)")
		ax.legend(road_names)
		
		return fig, ax
		
	def graph_intersection_crossings(self, intersection_index = None, style = "hexbin"):
		'''
		Draw graphs of times when intersection crossing events occured. Returns a list of (figure, axes) tuples. 
		Note that the intersection_index argument must be a list, even if only one index is specified, eg intersection_index = [0]. 
		Runs get_output if that method has not yet been run.
		'''
		self.run_output_conditional()
		data = self.output_dict["intersection_crossing_events"]
		out_fig_inter = []
				
		if intersection_index == None:
			intersection_index = range(len(self.intersections))
		
		for ii in intersection_index:
			subdata = data[ii]
# 			print subdata
			intersection = self.intersections[ii]
			
			fig = plt.figure()
			ax = fig.add_subplot(1,1,1)
			
			if style == "hexbin":
				diffs = np.diff(subdata)
# 				print diffs
				x_array = diffs[:-1]
				y_array = diffs[1:]
				# print x_array
# 				print y_array
				ax.hexbin(x_array, y_array)
				
				ax.set_xlabel("time before")
				ax.set_ylabel("time after")
				
			out_fig_inter.append((fig, ax))	
			
		return out_fig_inter
		
	def graph_removal_events(self, road_index = None, style = "hexbin"):
		'''
		Draw graphs of times when car removal events occured, i.e. a visualisation of when cars leave the system.
		'''
		self.run_output_conditional()
		data = self.output_dict["car_removal_events"]
		out_fig_rem = []
		
		if road_index == None:
			road_index = range(len(self.roads))
			
		for ii in road_index:
			road = self.roads[ii]
			subdata = data[ii]
			if not(any(subdata)):
				continue
							
			fig = plt.figure()
			ax = fig.add_subplot(1,1,1)
			
			if style == "hexbin":
				diffs = np.diff(subdata)
				x_array = diffs[:-1]
				y_array = diffs[1:]
				ax.hexbin(x_array, y_array)
				
				ax.set_xlabel("time before")
				ax.set_ylabel("time after")	
			
			out_fig_rem.append((fig, ax))
			
		return out_fig_rem
		
		
		
			
##