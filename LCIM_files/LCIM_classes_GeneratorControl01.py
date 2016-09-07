class GeneratorControl:
	def __init__(self):
		self.seed = np.random.randint(2147483647)
		
	def seed_generator(self, use_previous = True, custom_seed = None):
		if custom_seed:
			self.seed = custom_seed
		elif not(use_previous):
			self.seed = np.random.randint(2147483647)
		np.random.seed(self.seed)
		
	def get_seed(self):
		return self.seed



RndGen = GeneratorControl()


##