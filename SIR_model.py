import random as rd

class Agent():
	def __init__(self, pos=(0,0), max_x_range=10, max_y_range=10, sick=False, max_x_range=1):
		self.position = pos
		self.max_x_range = max_x_range
		self.max_y_range = max_y_range
		self.is_sick = sick
		self.moving_range = moving_range
		self.recovered = False

	def move(self):
		valid = False
		while not valid:
			try:
				x = rd.randrange(self.moving_range)
				y = rd.randrange(self.moving_range)
				assert self.position[0]+x <= self.max_x_range
				assert self.position[1]+y <= self.max_y_range
			except AssertionError:
				pass
			else:
				self.position = ( self.position[0]+x, self.position[1]+y )
				valid = True


class Controller:
	def __init__(self, n_agents=10, b_shape=(10,10), sick_agents=1, beta=0.6, gamma=0.6, disease_spread_distance=1,  time_steps=5):
		self.n_agents = n_agents
		self.b_shape = b_shape
		
		self.susceptibles = n_agents - sick_agents
		self.sick_agents = sick_agents
		self.recovered=0

		self.disease_spread_distance = disease_spread_distance
		self.beta=beta
		self.gamma=gamma
		
		self.agents = []
		self.crate_agents()
		with open('Disease_spread.csv', 'w') as new:
			new.write('Time step,Susceptibles,Infected,Recovered\n')
			new.write(f'0,{self.susceptibles},{sick_agents},0\n')

		for time_step in range(1, time_steps+1):
			self.time_step(time_step)

	def crate_agents(self):
		for _ in range(self.sick_agents):
			pos = (rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[0]))
			agent = Agent(pos, self.b_shape[0], self.b_shape[1], True)
			self.agents.append(agent)

		for _ in range(self.susceptibles):
			pos = (rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[0]))
			agent = Agent(pos, self.b_shape[0], self.b_shape[1])
			self.agents.append(agent)

	def agents_move(self):
		for agent in self.agents:
			agent.move()

	def agents_spread_disease(self):
		for agent in self.agents:
			pass

	def agents_recover(self):
		for agent in self.agents:
			if agent.is_sick and rd.random()>self.gamma:
				agent.is_sick=False
				agant.recovered=True

	def time_step(self, time_step):
		self.agents_move()
		self.agents_spread_disease()
		self.agents_recover()

		with open('Disease_spread.csv', 'a' ) as file:
			file.write(f'{time_step},{self.susceptibles},{self.sick_agents},{self.recovered}\n')

