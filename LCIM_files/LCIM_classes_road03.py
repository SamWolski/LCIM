#######################################
## road class version 03
## requires car version 02
## requires network version 03
## compatible with version 01 of all other classes

## changelog:
## 02: adds optional override following distances for roads (can artificially extend following distance on specific roads), via either variation in jam distance s0 or variation in safe time headway T
## 03: adds methods and variables to conform to standardised output


class Road:
	def __init__(self, name, length, priority = 0, T_factor = 1.0, s0 = 0.0, critical_distance = 1.0):
		## basic initialisation
		self.name = name
		self.length = length
		self.insertion_point = None
		
		## car handling
		self.cars = []
		self.s0 = s0
		self.T_factor = T_factor
		self.speed_limiter = 1.0
		
		## intersections
		self.priority = priority
		self.intersections = [None, None]
		self.critical_distance = critical_distance
		
		## output stats
		self.traffic_density = []
		self.average_velocity = []
		self.removal_events = []
		
	def add_insertion_point(self):
		'''
		Attaches the given insertion point to the beginning of the road.
		'''
		self.insertion_point = InsertionPoint(self)
		
	
	## road stats methods
	def update_traffic_density(self):
		td = float(len(self.cars))/self.length
		self.traffic_density.append(td)
	
	def update_average_velocity(self):
		if any(self.cars):
			av = float(sum([car.v[-1] for car in self.cars]))/len(self.cars)
			self.average_velocity.append(av)
		else:
			pass
		
	
	## display and output methods
	def setup_road_graph_pos(self, ax = None):
		'''
		Creates figure and axes used to graph car positions.
		'''
		if ax == None:
			fig, ax = plt.subplots()
		ax.set_xlabel("time")
		ax.set_ylabel("position")
		ax.set_ylim([0, self.length])
		return fig, ax
	def setup_road_graph_v(self, ax = None):
		'''
		Creates figure and axes used to graph car velocities.
		'''
		if ax == None:
			fig, ax = plt.subplots()
		ax.set_xlabel("time")
		ax.set_ylabel("velocity")
		return fig, ax	
				
		
##