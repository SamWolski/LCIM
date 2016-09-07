#######################################
## intersection class version 02
## requires car version 02
## requires road version 03
## requires network version 03
## compatible with version 01 of all other classes

## changelog:
## 02: adds infrastructure to log car passing events for output

class Intersection:
	def __init__(self, exit_road, entry_roads, network):
		## road connections
		self.exit_road = exit_road
		self.entry_roads = entry_roads
		
		## phantom car
		self.phantom_car = Car(0, 0, 0, 0, is_phantom = True)
		
		## car handling
		self.exit_car = None
		self.entry_cars = [None]*len(self.entry_roads)

		## intersections
		self.free_flow_entry = self.sort_roads()
		
		## stats
		self.network = network
		self.crossing_events = []

	def sort_roads(self):
		'''
		Called on initialisation, this method sorts the intersection's entry roads such that they are in descending order of priority, and checks if the highest-priority road is solitary, implying free flow from that channel. THe truth value of this is returned.
		'''
		self.entry_roads.sort(key = lambda x: x.priority, reverse = True)
		highest_priority = self.entry_roads[0].priority
		truthy = [xx.priority == highest_priority for xx in self.entry_roads]
		if truthy.count(True) > 1:
			return False
		else:
			return True

	def is_intersection_clear(self):
		'''
		Checks whether or not a car is physically blocking the intersection.
		'''
# 		print "Query: is intersection clear?"
		if self.exit_car == None:
			return True
		elif self.exit_car.inter_flag:
			return False
		else:
			d = self.exit_car.pos[-1] - self.exit_car.L
			if d <= 0.0:
				return False
			else:
				return True


	def do_car_passing(self, passing_car):
		'''
		Handles logistics of when a new car passes to the exit road. This method is a bit of a kludge, but does the job.
		'''
		# adds car passing event to stats
		self.crossing_events.append(self.network.time)
		
		# updating car details to be used with update method
		passing_car.inter_flag = True #uses intersection part of update method
		if self.exit_car == None:
			# free acceleration
			vdot = passing_car.get_vdot(None)
		else:
			vdot = max(passing_car.get_vdot(self.exit_car), 0)
		passing_car.new_v = passing_car.v[-1] + vdot*dt
		total_distance = passing_car.new_v*dt
		passing_car.inter_pos = total_distance - (passing_car.road.length - passing_car.pos[-1]) # to be updated properly in the update method
		# cleaning up exit car, passing car
		
		if passing_car.intersection[0]:
			passing_car.intersection[0].remove_exit_car()
# 		try:
# 			# if the passing car is also in the previous intersection, it is removed from being the exit car there.
# 			passing_car.intersection[0].remove_exit_car()
# 			pass
# 		except:
# 			pass
		elif passing_car.road.insertion_point and len(passing_car.road.cars) == 1:
# 			print "No other car on the road and insertion point exists.\nInsertion point's new leading car is None."
			passing_car.road.insertion_point.leading_car = None
		passing_car.intersection[0] = self
		passing_car.intersection[1] = self.exit_road.intersections[1]

		if not(self.exit_car == None):
			self.exit_car.following_car = passing_car
			self.exit_car.intersection[0] = None
		passing_car.leading_car = self.exit_car
		passing_car.road.cars.remove(passing_car)
		passing_car.road = self.exit_road
		passing_car.inter_flag = True
		self.exit_road.cars.append(passing_car)
		# modifying entry cars for intersection
		if passing_car.following_car:
			self.entry_cars = [passing_car.following_car if xx == passing_car else xx for xx in self.entry_cars]
		else:
			self.entry_cars = [None if xx == passing_car else xx for xx in self.entry_cars]
		for car in self.entry_cars:
			try:
				car.leading_car = passing_car
				car.intersection[1] = self
			except:
				pass
		## finally, change exit car for intersection
		self.exit_car = passing_car
		
	
	def remove_exit_car(self):
		'''
		Convenience wrapper for when the exit car is removed from the system.
		'''
		self.exit_car = None
		for entry_car in self.entry_cars:
			if entry_car:
				entry_car.leading_car = None
		

		
##