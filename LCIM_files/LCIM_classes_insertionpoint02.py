##
## version 02 adds a modification to the car addition code to enable cars to be placed on the road at maximum density

class InsertionPoint:
	def __init__(self, road):
		self.pending_cars = []
		self.road = road
		self.leading_car = None
		self.car_insertion_flag = False
	
	## car generation methods
	def generate_car(self):
		'''
		Generates a new car and places it in the queue
		'''
		new_car = Car(0.0, 0.0, 0, self.road, leading_intersection = None, leading_car = self.leading_car)
		self.pending_cars.append(new_car)
	
	
	## car placement methods - adding to system
	
	def is_road_clear(self):
		'''
		Check if the current last car is not physically blocking the road.
		'''
		if self.leading_car == None:
			return True
		elif self.leading_car.pos[-1] - self.leading_car.L <= 0.0:
			return False
		else:
			return True
		
	def can_add_car(self):
		'''
		Assess whether the next pending car can be added (intelligently).
		'''
		new_car = self.pending_cars[0]			
# 		vdot = self.pending_cars[0].get_vdot(self.leading_car)
# 		print new_car.v
		new_car.v[-1] = min(self.leading_car.v[-1], new_car.u)
# 		print new_car.v
		vdot = new_car.get_vdot(self.leading_car)
# 		print vdot
		if vdot >= -new_car.b:
			return True
		else:
			return False
		
# 		
# 		if any(self.pending_cars):
# 			new_car = self.pending_cars[0]
# 			d = (self.leading_car.pos[-1] - self.leading_car.L) - (new_car.v[-1]*new_car.T + new_car.s[0])
# 			if d >= 0.0:
# # 				return True
# 				new_v = new_car.get_vdot(self.leading_car)
# 				if new_v > 0.0:
# 					return True
# 				else:
# 					return False
# 			else:
# 				return False
# 		else:
# 			return False
		
			
##