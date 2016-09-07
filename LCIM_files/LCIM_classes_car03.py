#######################################
## car class version 03
## requires road, network version 02
## compatible with version 01 of all other classes

## changelog:
## 02: adds optional override following distances for roads (can artificially extend following distance on specific roads), via either variation in jam distance s0 or variation in safe time headway T
## 03: generator functions for parameters migrated to separate file (parameter_dists01.py)

class Car:
	# car ID generator function
	new_car_id = itertools.count().next
	
	def __init__(self, x, v, creation_time, road, leading_intersection = None, leading_car = None, is_phantom = False):
		## car details
		if not is_phantom:
			self.ID = Car.new_car_id()
			self.is_phantom = False
		else:
			self.is_phantom = True
			self.ID = 999999
		self.leading_car = leading_car
		self.following_car = None
		self.road = road
		self.intersection = [None, leading_intersection]
		
		## parameter generation
		self.a = generate_acceleration()
		self.b = generate_braking()
		self.u = generate_desired_velocity()
		self.L = generate_car_length()
		self.T = generate_safe_time_headway()
		self.s = generate_jam_distance()
		self.tau = generate_reaction_time()
		self.beta = generate_braking_threshold()
		self.omega = generate_overbraking_factor()
		self.J = generate_joining_braking_factor()
		self.c = generate_continuation_factor()

		## simulation mechanics
		self.pos = []
		self.pos.append(x)
		self.pos_road = []
		self.pos_road.append(road)
		self.v = []
		self.v.append(v)
		self.new_v = v
		self.creation_time = creation_time
		self.removal_time = None
		self.time_iterations = [creation_time]
		# intersection-specific variables
		self.inter_pos = 0.0
		self.inter_flag = False
		
	
	
	## calculation functions
		
	def get_dxstar(self, leading_car):
		'''
		Get the dynamically-adjusted ``optimal distance'' based on the car this method is called from, and the specified leading car.
		'''
		if leading_car.is_phantom:
			dV = self.v[-1]
			s0 = self.s[0] 
			T = self.T
		else:
			try:
				retarded_velocity = leading_car.v[-1 - self.tau]
			except:
# 				print "********************"
# 				print "Error 2: leading car velocity history for car ID", self.ID, "does not extend sufficiently for reaction time to be applied.\nReaction time:", self.tau, "\nLeading car position history length:", len(leading_car.v)
				retarded_velocity = leading_car.v[-1]
			dV = self.v[-1] - retarded_velocity
			s0 = max(self.s[0], leading_car.road.s0) # artificial following distance
			T = self.T*leading_car.road.T_factor # artificial safe time headway
		if self.is_in_critical_distance():
			u = self.u*self.intersection[1].exit_road.speed_limiter
		else:
			u = self.u*self.road.speed_limiter
		dxstar = s0 + self.s[1]*np.sqrt(self.v[-1]/u) + T*self.v[-1] + (self.v[-1]*dV)/(2*np.sqrt(self.a*self.b))
		return dxstar

	def get_vdot(self, leading_car):
		'''
		Get the calculated new velocity for the car this method is called from, based on the leading car.
		
		This is calculated according to the Intelligent Driver Model proposed by M Treiber et al.
		'''
		if leading_car == None:
			dxs = 0.0
			dx = 1.0
		elif leading_car.is_phantom == True:
			dx = self.road.length - self.pos[-1] + self.s[0]
			dxs = self.get_dxstar(leading_car)
		elif not(leading_car.road == self.road) or (not(leading_car.pos_road[-1 - self.tau] == self.road) if len(leading_car.pos_road) > 1+self.tau else False):
			# occurs during intersection passage
			dx = (self.road.length - self.pos[-1]) + leading_car.pos[-1 - self.tau] - leading_car.L
			dxs = self.get_dxstar(leading_car)
		else:
			try:
				retarded_pos = leading_car.pos[-1 - self.tau]
			except:
				# print "********************"
# 				print "Error 1: leading car position history for car ID", self.ID, "does not extend sufficiently for reaction time to be applied.\nReaction time:", self.tau, "\nLeading car position history length:", len(leading_car.pos)
				retarded_pos = leading_car.pos[-1]
			dx = retarded_pos - leading_car.L - self.pos[-1]
			dxs = self.get_dxstar(leading_car)
		if self.is_in_critical_distance():
			u = self.u*self.intersection[1].exit_road.speed_limiter
		else:
			u = self.u*self.road.speed_limiter
		vdot = self.a*(1. - (self.v[-1]/u)**delta - (dxs/dx)**2)
		return vdot
	
	def calculate_new_velocity(self, leading_car = None):
		'''
		Calculate the new velocity for the given car with specified leading car, defaulting to the assigned leading car. The new velocity is stored, but not immediately updated.
		
		If the new velocity is negative, it is modified to 0.0 and the car remains stationary.
		'''
		if leading_car == None:
			leading_car = self.leading_car
		vdot = self.get_vdot(leading_car)
		if (vdot < 0.0) and (self.v[-1] < self.beta): #and (abs(vdot) < self.beta):
			self.new_v = 0.0
# 			vdot = vdot*self.omega*(1+1./self.v[-1])
		else:
			new_v = self.v[-1] + vdot*dt
			self.new_v = max(0.0, self.v[-1] + vdot*dt)		
	
	# calculate the time it would take to accelerate to a given velocity with free acceleration		
	def t_from_v(self, following_car = None):
		if following_car:
			return (following_car.v[-1]/self.a)*hyp2f1(1., 1./delta, 1+1./delta, (following_car.v[-1]/self.u)**delta)
		else:
			return 0.0
			
			
	## simulation and iteration functions
	def set_creation_time(self, new_time):
		'''
		Setting custom creation time for car. Used when car has been initialised before it has been placed in the system.
		'''
		self.creation_time = new_time
		self.time_iterations = [new_time]
	
	
	def check_removal(self):
		'''
		Checks if the car will exit the bounds of a road (which does not terminate in an intersection) on the next iteration.
		'''
# 		keyID = None
# 		printout = False
# 		if self.ID == keyID: printout = True	
		if self.is_phantom:
# 			if printout: print "Car ", keyID, "is phantom"
			return False
		elif self.intersection[1] or self.inter_flag: #or self.inter_flag:
# 			if printout: print "Car", keyID, "has an intersection at the end of its road"
			return False
# 		elif self.inter_flag:
# 			if printout: print "Car", keyID, "is currently passing through an intersection"
# 			return False
		elif self.pos[-1] + self.new_v*dt <= self.road.length:
# 			if printout: print "Car", keyID, "is not travelling far enough to be removed on ", self.road.name
			return False
		else:
# 			if printout: print "Car", keyID, "is not being removed"
			return True
		
	def update(self, time):
		'''
		Updates the car, applying the changes that had been previously calculated (position and velocity updates). This takes into account the road-switching that occurs when going through an intersection.
		'''
		if self.is_phantom:
			pass
		else:
			self.pos_road.append(self.road)
			self.v.append(self.new_v)
			self.time_iterations.append(time)
			if self.inter_flag:
				self.pos.append(self.inter_pos)
				self.inter_flag = False
			else:
				self.pos.append(self.pos[-1] + self.new_v*dt)
			
	## intersection-related functions
	def is_in_intersection(self):
		'''
		Checks if the car is in an intersection. Effectively checks whether it is the last or first car on the road.
		'''
		return any(self.intersection)
	def leading_car_is_in_intersection(self):
		'''
		If a leading car exists, checks if it is in an intersection (ie is the last or first car on the road). Default (leading car is None) returns False.
		'''
		try:
			return self.leading_car.is_in_intersection()
		except:
			return False
			
	def check_intersection_point_passing(self):
		'''
		Checks if the car will physically pass the intersection point on the next iteration.
		'''
		if self.new_v*dt + self.pos[-1] > self.road.length:
			return True
		return False
		
	def evaluate_safe_distance(self, exit_car):
		'''
		Check if there is enough space such that the car pulling out will maintain safe time headway behind the leading car. Default (if there is no car in the exit road of the intersection) is True.
		'''
		if exit_car == None:
			return True
		elif not(exit_car.pos_road[-1 - self.tau] == self.intersection[1].exit_road):
			return False
		sd = (exit_car.pos[-1 - self.tau] - exit_car.L) - (self.v[-1]*self.T + self.s[0])
		if sd >= 0.0:
			return True
		else:
			return False
		
	def is_in_critical_distance(self):
		return (self.intersection[1]) and (self.pos[-1] + self.road.critical_distance >= self.road.length)
	
	def can_pull_out_safely(self):
		'''
		Check if the car can pull out of the intersection. Checks, in order, if
		 - the car is close enough to the intersection to realistically consider pulling out
		 - the intersection is not obstructed (ie another car is not physically occupying the space)
		 - there is enough distance behind the exit car such that the car can pull out safely (checked using the evaluate_safe_distance method)
		 - cars on roads of equal priority will take a longer time to reach the intersection than this car
		 - cars on higher-priority roads will evaluate an acceleration which will not be less than a factor of their comfortable braking rate
		If none of the disqualifyiing criteria apply, returns True
		'''
		## check critical distance - is car close enough to intersection?
		if not(self.is_in_critical_distance()):
# 			print "Car", self.ID, "not within critical distance, pos is", self.pos[-1]
			return False
		## check obstruction of intersection
		elif not(self.intersection[1].is_intersection_clear()):
# 			print "Car", self.ID, "intersection not clear, pos is", self.pos[-1]
			return False
		## check safe distance to car in front (intersection exit car)
		elif not(self.evaluate_safe_distance(self.intersection[1].exit_car)):
# 			print "Car", self.ID, "not enough safe distance, pos is", self.pos[-1]
			return False
		## check appropriate space on intersection entry roads
		for road, other_car in zip(self.intersection[1].entry_roads, self.intersection[1].entry_cars):
			if road.priority < self.road.priority:
				continue
			elif road.priority == self.road.priority:
				if road == self.road:
					continue
				else:
					if any(road.cars):
						if other_car.inter_flag:
							return False
						elif other_car.is_in_critical_distance():#(other_car.pos[-1] + other_car.road.critical_distance < other_car.road.length):
							continue
						own_time = (self.road.length - self.pos[-1])/self.v[-1]
						if other_car.v[-1]:							
							other_time = (other_car.road.length - other_car.pos[-1])/other_car.v[-1]
							if own_time > other_time:
								return False
							else:
								continue
						else: # the other car is stationary but not in range of the intersection for some reason
							continue
					else:
						continue
			# higher-priorirty roads 
			elif road.priority > self.road.priority:
				if any(road.cars):				
					# work out if the oncoming car will have enough time headway
# 					other_car = road.cars[0]
# 					oncoming_distance = road.length - oncoming_car.pos[-1]
# 					if (oncoming_distance < 1.0*oncoming_car.L) and (oncoming_car.v[-1] < ):
# 						if oncoming_car.inter_flag:
# 							return False
# 						elif (oncoming_car.pos[-1] + oncoming_car.road.critical_distance < oncoming_car.road.length):
# 							continue
# 						own_time = (self.road.length - self.pos[-1])/self.v[-1]
# 						if oncoming_car.v[-1]:
# 							other_time = (oncoming_car.road.length - oncoming_car.pos[-1])/oncoming_car.v[-1]
# 							if own_time > other_time:
# 								return False
# 							else:
# 								continue
# 					else:
					# work out if there is enough spacing for the oncoming vehicle
					test_vdot = other_car.get_vdot(self.intersection[1].phantom_car)
					# check if deceleration is acceptable
					try:
						retarded_v = other_car.v[-1 - self.tau]
					except:
						retarded_v = other_car.v[-1]
					if test_vdot < -(other_car.J*other_car.b):
						# car would have to brake too hard
						return False
					# check if car would have to slow down below own desired velocity on the road
					elif (retarded_v + test_vdot*dt) <= self.u*self.road.speed_limiter:#other_car.c*other_car.u:
						return False
# 					elif oncoming_car.v[-1] <= oncoming_car.c*oncoming_car.u:
# 						return False
					else:
						continue
				else:
					continue
						
					
										
		## nothing caught - seems safe!	
		return True
		
	
	def do_pull_out(self):
		'''
		Alias for car passing.
		'''
		self.intersection[1].do_car_passing(self)
		
	
##